
from django.contrib import admin
from django.forms import MultipleChoiceField, ModelForm
from django.forms.widgets import CheckboxSelectMultiple

from forms_builder.models import BuiltForm, BuiltFormSubmission
from forms_builder.utils import form_builder_optional_fields


class OptionalFieldsField(MultipleChoiceField):
	"""
	extend MultipleChoiceField to quote returned value for db
	"""
	
	def __init__(self, *args, **kwargs):
		kwargs["widget"] = OptionalFieldsWidget
		kwargs["choices"] = form_builder_optional_fields()
		super(OptionalFieldsField, self).__init__(*args, **kwargs)
	
	def clean(self, value):
		return "\"%s\"" % value


class OptionalFieldsWidget(CheckboxSelectMultiple):
	"""
	extend CheckboxSelectMultiple to unquote value for widget
	"""
	
	def render(self, name, value, **kwargs):
		if value and hasattr(value, "strip"):
			value = eval(value.strip("\""))
		return super(OptionalFieldsWidget, self).render(name, value, **kwargs)


class BuiltFormAdminForm(ModelForm):
	"""
	creates a multi-checkbox admin form field using the optional fields
	from the BuiltFormSubmission model
	"""
	
	mandatory_extra_fields = OptionalFieldsField()
	optional_extra_fields = OptionalFieldsField()


class BuiltFormAdmin(admin.ModelAdmin):
	
	form = BuiltFormAdminForm
	
	class Media:
		css = {"all": ("admin/fix-multi-checkbox.css",)}
			

class BuiltFormSubmissionAdmin(admin.ModelAdmin):
	
	list_display = ("built_form", "first_name", "last_name", "email", 
		"submission_date")
	list_filter = ("built_form",)
	search_fields = ("first_name", "last_name", "email",)


admin.site.register(BuiltForm, BuiltFormAdmin)
admin.site.register(BuiltFormSubmission, BuiltFormSubmissionAdmin)
