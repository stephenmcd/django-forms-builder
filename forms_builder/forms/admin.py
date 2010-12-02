
from csv import writer
from datetime import datetime
from mimetypes import guess_type
from os.path import join

from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from forms_builder.forms.forms import ExportForm
from forms_builder.forms.models import Form, Field, FieldEntry
from forms_builder.forms.settings import UPLOAD_ROOT, USE_SITES


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
    list_display = ("title", "status", "email_copies",
        "publish_date", "expiry_date", "admin_link_export", "admin_link_view")
    list_display_links = ("title",)
    list_editable = ("status", "email_copies", "publish_date", "expiry_date")
    list_filter = ("status",)
    filter_horizontal = form_admin_filter_horizontal
    search_fields = ("title", "intro", "response", "email_from",
        "email_copies")
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = form_admin_fieldsets

    def get_urls(self):
        """
        Add the export view to urls.
        """
        urls = super(FormAdmin, self).get_urls()
        extra_urls = patterns("",
            url("^export/(?P<form_id>\d+)/$",
                self.admin_site.admin_view(self.export_view),
                name="form_export"),
            url("^file/(?P<field_entry_id>\d+)/$",
                self.admin_site.admin_view(self.file_view),
                name="form_file"),
        )
        return extra_urls + urls

    def export_view(self, request, form_id):
        """
        Output a CSV file to the browser containing the entries for the form.
        """
        if request.POST.get("back"):
            change_url = reverse("admin:%s_%s_change" %
                (Form._meta.app_label, Form.__name__.lower()), args=(form_id,))
            return HttpResponseRedirect(change_url)
        form = get_object_or_404(Form, id=form_id)
        export_form = ExportForm(form, request, request.POST or None)
        if export_form.is_valid():
            response = HttpResponse(mimetype="text/csv")
            fname = "%s-%s.csv" % (form.slug, slugify(datetime.now().ctime()))
            response["Content-Disposition"] = "attachment; filename=%s" % fname
            csv = writer(response)
            csv.writerow(export_form.columns())
            for rows in export_form.rows():
                csv.writerow(rows)
            return response
        template = "admin/forms/export.html"
        context = {"title": _("Export Entries"), "export_form": export_form}
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
