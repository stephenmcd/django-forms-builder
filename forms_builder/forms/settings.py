
from django.conf import settings


# The maximum allowed length for field values.
FIELD_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_FIELD_MAX_LENGTH", 2000)

# The maximum allowed length for field labels.
LABEL_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_LABEL_MAX_LENGTH", 20)

# The absolute path where files will be uploaded to.
UPLOAD_ROOT = getattr(settings, "FORMS_BUILDER_UPLOAD_ROOT", None)

# Boolean controlling whether forms are associated to Django's Sites framework.
USE_SITES = getattr(settings, "FORMS_BUILDER_USE_SITES", 
    "django.contrib.sites" in settings.INSTALLED_APPS)
