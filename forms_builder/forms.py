
from datetime import date

from django import forms
from django.forms.extras import SelectDateWidget

from forms_builder.models import BuiltForm, BuiltFormSubmission
from forms_builder.utils import form_builder_optional_fields


class DobWidget(SelectDateWidget):
	"""
	populate the years of a SelectDateWidget for selecting dob
	"""
	
	def __init__(self, attrs=None):
		year = date.today().year
		self.attrs = attrs
		self.years = range(year, year - 100, -1)
		super(SelectDateWidget, self).__init__()


def get_built_form_form(built_form):
	"""
	return a model form for a BuiltFormSubmission, excluding the extra
	fields that haven't been selected as optional or mandatory for the given 
	BuiltForm, and setting the extra mandatory fields that have been selected 
	as mandatory fields
	"""
	
	dob_field = None
	extra_fields = (built_form.extra_fields("mandatory") + 
		built_form.extra_fields("optional"))
	if "dob" in extra_fields:
		dob_field = forms.DateField(widget=DobWidget)

	class BuiltFormForm(forms.ModelForm):
	
		class Meta:
			model = BuiltFormSubmission
			exclude = ["submission_date","built_form"] + [field[0] for field in 
				form_builder_optional_fields() if field[0] not in extra_fields]
			
		dob = dob_field
		
		def __init__(self, *args, **kwargs):
			super(BuiltFormForm, self).__init__(*args, **kwargs)
			for field in built_form.extra_fields("mandatory"):
				self.fields[field].required = True
				if hasattr(self.fields[field], "choices"):
					self.fields[field].choices = self.fields[field].choices[1:]

	return BuiltFormForm