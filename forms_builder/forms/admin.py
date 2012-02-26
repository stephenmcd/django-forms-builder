
from csv import writer
from datetime import datetime
from mimetypes import guess_type
from os.path import join
from cStringIO import StringIO

from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.translation import ungettext, ugettext_lazy as _

from forms_builder.forms.forms import EntriesForm
from forms_builder.forms.models import Form, Field, FormEntry, FieldEntry
from forms_builder.forms.settings import CSV_DELIMITER, UPLOAD_ROOT, USE_SITES


fs = FileSystemStorage(location=UPLOAD_ROOT)
form_admin_filter_horizontal = ()
form_admin_fieldsets = [
    (None, {"fields": ("title", ("status", "login_required",),
        ("publish_date", "expiry_date",), "intro", "button_text", "response")}),
    (_("Email"), {"fields": ("send_email", "email_from", "email_copies",
        "email_subject", "email_message")}),]

if USE_SITES:
    form_admin_fieldsets.append((_("Sites"), {"fields": ("sites",),
        "classes": ("collapse",)}))
    form_admin_filter_horizontal = ("sites",)

class FieldAdmin(admin.TabularInline):
    model = Field

class FormAdmin(admin.ModelAdmin):

    inlines = (FieldAdmin,)
    list_display = ("title", "status", "email_copies", "publish_date",
                    "expiry_date", "total_entries", "admin_links")
    list_display_links = ("title",)
    list_editable = ("status", "email_copies", "publish_date", "expiry_date")
    list_filter = ("status",)
    filter_horizontal = form_admin_filter_horizontal
    search_fields = ("title", "intro", "response", "email_from",
                     "email_copies")
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = form_admin_fieldsets

    def queryset(self, request):
        """
        Annotate the queryset with the entries count for use in the
        admin list view.
        """
        qs = super(FormAdmin, self).queryset(request)
        return qs.annotate(total_entries=Count("entries"))

    def get_urls(self):
        """
        Add the entries view to urls.
        """
        urls = super(FormAdmin, self).get_urls()
        extra_urls = patterns("",
            url("^(?P<form_id>\d+)/entries/$",
                self.admin_site.admin_view(self.entries_view),
                name="form_entries"),
            url("^(?P<form_id>\d+)/entries/show/$",
                self.admin_site.admin_view(self.entries_view),
                {"show": True}, name="form_entries_show"),
            url("^(?P<form_id>\d+)/entries/export/$",
                self.admin_site.admin_view(self.entries_view),
                {"export": True}, name="form_entries_export"),
            url("^file/(?P<field_entry_id>\d+)/$",
                self.admin_site.admin_view(self.file_view),
                name="form_file"),
        )
        return extra_urls + urls

    def entries_view(self, request, form_id, show=False, export=False):
        """
        Displays the form entries in a HTML table with option to
        export as CSV file.
        """
        if request.POST.get("back"):
            change_url = reverse("admin:%s_%s_change" %
                (Form._meta.app_label, Form.__name__.lower()), args=(form_id,))
            return HttpResponseRedirect(change_url)
        form = get_object_or_404(Form, id=form_id)
        entries_form = EntriesForm(form, request, request.POST or None)
        delete_entries_perm = "%s.delete_formentry" % FormEntry._meta.app_label
        can_delete_entries = request.user.has_perm(delete_entries_perm)
        submitted = entries_form.is_valid() or show or export
        export = export or request.POST.get("export")
        if submitted:
            if export:
                response = HttpResponse(mimetype="text/csv")
                fname = "%s-%s.csv" % (form.slug, slugify(datetime.now().ctime()))
                response["Content-Disposition"] = "attachment; filename=%s" % fname
                queue = StringIO()
                csv = writer(queue, delimiter=CSV_DELIMITER)
                csv.writerow(entries_form.columns())
                for row in entries_form.rows(csv=True):
                    csv.writerow(row)
                # Decode and reencode entire queued response into utf-16 to be Excel compatible
                data = queue.getvalue().decode("utf-8").encode("utf-16")
                response.write(data)
                return response
            elif request.POST.get("delete") and can_delete_entries:
                selected = request.POST.getlist("selected")
                if selected:
                    try:
                        from django.contrib.messages import info
                    except ImportError:
                        def info(request, message, fail_silently=True):
                            request.user.message_set.create(message=message)
                    entries = FormEntry.objects.filter(id__in=selected)
                    count = entries.count()
                    if count > 0:
                        entries.delete()
                        message = ungettext("1 entry deleted",
                                            "%(count)s entries deleted", count)
                        info(request, message % {"count": count})
        template = "admin/forms/entries.html"
        context = {"title": _("View Entries"), "entries_form": entries_form,
                   "opts": self.model._meta, "original": form,
                   "can_delete_entries": can_delete_entries,
                   "submitted": submitted}
        return render_to_response(template, context, RequestContext(request))

    def file_view(self, request, field_entry_id):
        """
        Output the file for the requested field entry.
        """
        field_entry = get_object_or_404(FieldEntry, id=field_entry_id)
        path = join(fs.location, field_entry.value)
        response = HttpResponse(mimetype=guess_type(path)[0])
        f = open(path, "r+b")
        response["Content-Disposition"] = "attachment; filename=%s" % f.name
        response.write(f.read())
        f.close()
        return response

admin.site.register(Form, FormAdmin)
