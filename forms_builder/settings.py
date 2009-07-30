
from django.conf import settings


UPLOAD_TO = getattr(settings, "FORMS_BUILDER_UPLOAD_TO", "formsbuilder_uploads")
EMAIL_TO = getattr(settings, "FORMS_BUILDER_EMAIL_TO", None)