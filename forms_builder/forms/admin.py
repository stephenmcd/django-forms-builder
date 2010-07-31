
from csv import writer
from datetime import datetime

from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader, Context
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from forms_builder.forms.models import Form, Field, FieldEntry
from forms_builder.forms.utils import FormEntryExport

    
class FieldAdmin(admin.TabularInline):
    model = Field

class FormAdmin(admin.ModelAdmin):

    inlines = (FieldAdmin,)
    list_display = ("title", "status", "email_from", "email_copies", 
        "admin_link_export", "admin_link_view")
    list_display_links = ("title",)
    list_editable = ("status", "email_from", "email_copies")
    list_filter = ("status",)
    search_fields = ("title", "intro", "response", "email_from", 
        "email_copies")
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = (
        (None, {"fields": ("title", "status", "intro", "response")}),
        (_("Email"), {"fields": ("send_email", "email_from", "email_copies")}),
    )

    def get_urls(self):
        """
        Add the export view to urls.
        """
        urls = super(FormAdmin, self).get_urls()
        extra_urls = patterns("", 
            url("^export/(?P<form_id>\d+)/$", 
                self.admin_site.admin_view(self.export_view), 
                name="form_export"),
        )
        return extra_urls + urls

    def export_view(self, request, form_id):
        """
        Output a CSV file to the browser containing the entries for the form. 
        """
        form = get_object_or_404(Form, id=form_id)
        response = HttpResponse(mimetype="text/csv")
        csvname = "%s-%s.csv" % (form.slug, slugify(datetime.now().ctime()))
        response["Content-Disposition"] = "attachment; filename=%s" % csvname
        csv = writer(response)
        # Write out the column names and store the index of each field 
        # against its ID for building each entry row.
        columns = []
        field_indexes = {}
        for field in form.fields.all():
            columns.append(field.label.encode("utf-8"))
            field_indexes[field.id] = len(field_indexes)
        csv.writerow(columns)
        # Loop through each field value order by entry, building up each  
        # entry as a row.
        current_entry = None
        current_row = None
        values = FieldEntry.objects.filter(entry__form=form)
        for field_entry in values.order_by("-entry__id"):
            if field_entry.entry_id != current_entry:
                # New entry, write out the current row and start a new one.
                current_entry = field_entry.entry_id
                if current_row is not None:
                    csv.writerow(current_row)
                current_row = [""] * len(columns)
            # Only use values for fields that currently exist for the form.
            value = field_entry.value.encode("utf-8")
            try:
                current_row[field_indexes[field_entry.field_id]] = value
            except KeyError:
                pass
        # Write out the final row.
        if current_row is not None:
            csv.writerow(current_row)
        return response        

admin.site.register(Form, FormAdmin)

