from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from forms_builder.forms import models as forms_models


class Forms(CMSPlugin):
    form = models.ForeignKey(forms_models.Form, verbose_name=_('Form'))
