from __future__ import unicode_literals
from future.builtins import bytes, open

from csv import writer
from mimetypes import guess_type
from os.path import join
from datetime import datetime
from io import BytesIO, StringIO

from django.contrib import admin
from django.core.files.storage import FileSystemStorage
try:
    from django.urls import reverse, re_path
except ImportError:
    # For django 1.8 compatiblity
    from django.conf.urls import url as re_path
    from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ungettext, ugettext_lazy as _

from forms_builder.forms.forms import EntriesForm
from forms_builder.forms.models import Form, Field, FormEntry, FieldEntry
from forms_builder.forms.settings import CSV_DELIMITER, UPLOAD_ROOT
from forms_builder.forms.settings import USE_SITES, EDITABLE_SLUGS
from forms_builder.forms.utils import now, slugify

try:
    import xlwt
    XLWT_INSTALLED = True
    XLWT_DATETIME_STYLE = xlwt.easyxf(num_format_str='MM/DD/YYYY HH:MM:SS')
except ImportError:
    XLWT_INSTALLED = False


fs = FileSystemStorage(location=UPLOAD_ROOT)
form_admin_filter_horizontal = ()
form_admin_fieldsets = [
    (None, {"fields": ("title", ("status", "login_required",),
        ("publish_date", "expiry_date",),
        "intro", "button_text", "response", "redirect_url")}),
    (_("Email"), {"fields": ("send_email", "email_from", "email_copies",
        "email_subject", "email_message")}),]

if EDITABLE_SLUGS:
    form_admin_fieldsets.append(
            (_("Slug"), {"fields": ("slug",), "classes": ("collapse",)}))

if USE_SITES:
    form_admin_fieldsets.append((_("Sites"), {"fields": ("sites",),
        "classes": ("collapse",)}))
    form_admin_filter_horizontal = ("sites",)


class FieldAdmin(admin.TabularInline):
    model = Field
    exclude = ('slug', )


class FormAdmin(admin.ModelAdmin):
    formentry_model = FormEntry
    fieldentry_model = FieldEntry

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

    def get_queryset(self, request):
        """
        Annotate the queryset with the entries count for use in the
        admin list view.
        """
        qs = super(FormAdmin, self).get_queryset(request)
        return qs.annotate(total_entries=Count("entries"))

    def get_urls(self):
        """
        Add the entries view to urls.
        """
        urls = super(FormAdmin, self).get_urls()
        extra_urls = [
            re_path("^(?P<form_id>\d+)/entries/$",
                self.admin_site.admin_view(self.entries_view),
                name="form_entries"),
            re_path("^(?P<form_id>\d+)/entries/show/$",
                self.admin_site.admin_view(self.entries_view),
                {"show": True}, name="form_entries_show"),
            re_path("^(?P<form_id>\d+)/entries/export/$",
                self.admin_site.admin_view(self.entries_view),
                {"export": True}, name="form_entries_export"),
            re_path("^file/(?P<field_entry_id>\d+)/$",
                self.admin_site.admin_view(self.file_view),
                name="form_file"),
        ]
        return extra_urls + urls

    def entries_view(self, request, form_id, show=False, export=False,
                     export_xls=False):
        """
        Displays the form entries in a HTML table with option to
        export as CSV file.
        """
        if request.POST.get("back"):
            bits = (self.model._meta.app_label, self.model.__name__.lower())
            change_url = reverse("admin:%s_%s_change" % bits, args=(form_id,))
            return HttpResponseRedirect(change_url)
        form = get_object_or_404(self.model, id=form_id)
        post = request.POST or None
        args = form, request, self.formentry_model, self.fieldentry_model, post
        entries_form = EntriesForm(*args)
        delete = "%s.delete_formentry" % self.formentry_model._meta.app_label
        can_delete_entries = request.user.has_perm(delete)
        submitted = entries_form.is_valid() or show or export or export_xls
        export = export or request.POST.get("export")
        export_xls = export_xls or request.POST.get("export_xls")
        if submitted:
            if export:
                response = HttpResponse(content_type="text/csv")
                fname = "%s-%s.csv" % (form.slug, slugify(now().ctime()))
                attachment = "attachment; filename=%s" % fname
                response["Content-Disposition"] = attachment
                queue = StringIO()
                try:
                    csv = writer(queue, delimiter=CSV_DELIMITER)
                    writerow = csv.writerow
                except TypeError:
                    queue = BytesIO()
                    delimiter = bytes(CSV_DELIMITER, encoding="utf-8")
                    csv = writer(queue, delimiter=delimiter)
                    writerow = lambda row: csv.writerow([c.encode("utf-8")
                        if hasattr(c, "encode") else c for c in row])
                writerow(entries_form.columns())
                for row in entries_form.rows(csv=True):
                    writerow(row)
                data = queue.getvalue()
                response.write(data)
                return response
            elif XLWT_INSTALLED and export_xls:
                response = HttpResponse(content_type="application/vnd.ms-excel")
                fname = "%s-%s.xls" % (form.slug, slugify(now().ctime()))
                attachment = "attachment; filename=%s" % fname
                response["Content-Disposition"] = attachment
                queue = BytesIO()
                workbook = xlwt.Workbook(encoding='utf8')
                sheet = workbook.add_sheet(form.title[:31])
                for c, col in enumerate(entries_form.columns()):
                    sheet.write(0, c, col)
                for r, row in enumerate(entries_form.rows(csv=True)):
                    for c, item in enumerate(row):
                        if isinstance(item, datetime):
                            item = item.replace(tzinfo=None)
                            sheet.write(r + 2, c, item, XLWT_DATETIME_STYLE)
                        else:
                            sheet.write(r + 2, c, item)
                workbook.save(queue)
                data = queue.getvalue()
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
                    entries = self.formentry_model.objects.filter(id__in=selected)
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
                   "submitted": submitted,
                   "xlwt_installed": XLWT_INSTALLED}
        return render(request, template, context)

    def file_view(self, request, field_entry_id):
        """
        Output the file for the requested field entry.
        """
        model = self.fieldentry_model
        field_entry = get_object_or_404(model, id=field_entry_id)
        path = join(fs.location, field_entry.value)
        response = HttpResponse(content_type=guess_type(path)[0])
        f = open(path, "r+b")
        response["Content-Disposition"] = "attachment; filename=%s" % f.name
        response.write(f.read())
        f.close()
        return response


admin.site.register(Form, FormAdmin)
