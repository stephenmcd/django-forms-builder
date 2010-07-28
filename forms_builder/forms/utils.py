
from django.shortcuts import get_object_or_404

from forms_builder.forms.models import Form, STATUS_PUBLIC


def get_form(request, slug):
    """
    Wrap get_object_or_404 with a check against status for non-staff users.
    """
    queryset = Form.objects.all()
    if not request.user.is_staff:
        queryset = queryset.filter(status=STATUS_PUBLIC)
    return get_object_or_404(queryset, slug=slug)
