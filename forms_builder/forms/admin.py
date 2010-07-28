
from django.contrib import admin

from forms_builder.forms.models import Form, Field


class FieldAdmin(admin.TabularInline):
    model = Field

class FormAdmin(admin.ModelAdmin):
    inlines = (FieldAdmin,)


admin.site.register(Form, FormAdmin)

