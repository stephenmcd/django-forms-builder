
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from forms_builder.forms.models import Form, Field


class FieldAdmin(admin.TabularInline):
    model = Field

class FormAdmin(admin.ModelAdmin):
    inlines = (FieldAdmin,)
    list_display = ("title","status","email_from","email_copies","admin_link")
    list_display_links = ("title",)
    list_editable = ("status","email_from","email_copies")
    list_filter = ("status",)
    search_fields = ("title","intro","response","email_from","email_copies")
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = (
        (None, {"fields": ("title", "status", "intro", "response")}),
        (_("Email"), {"fields": ("send_email", "email_from", "email_copies")}),
    )

admin.site.register(Form, FormAdmin)

