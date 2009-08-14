
from django.shortcuts import get_object_or_404

from forms_builder.models import BuiltForm, BuiltFormSubmission, STATUS_PUBLIC


def form_builder_optional_fields():
	"""
	return the field name / verbose name pairs for all fields in 
	BuiltFormSubmission that are considered optional, eg blank=True
	"""

	meta = BuiltFormSubmission._meta
	return [(field.name, field.verbose_name) for field in meta.fields 
		if field.blank and field != meta.pk]	


def get_built_form(request, slug):
	"""
	wrap get_object_or_404 with a check against status if the user is not staff
	"""
	
	queryset = BuiltForm.objects.all()
	if not request.user.is_staff:
		queryset = queryset.filter(status=STATUS_PUBLIC)
	return get_object_or_404(queryset, slug=slug)