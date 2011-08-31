
from django.conf import settings


# The maximum allowed length for field values.
FIELD_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_FIELD_MAX_LENGTH", 2000)

# The maximum allowed length for field labels.
LABEL_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_LABEL_MAX_LENGTH", 200)

# The absolute path where files will be uploaded to.
UPLOAD_ROOT = getattr(settings, "FORMS_BUILDER_UPLOAD_ROOT", None)

# Boolean controlling whether HTML5 form fields are used.
USE_HTML5 = getattr(settings, "FORMS_BUILDER_USE_HTML5", True)

# Boolean controlling whether forms are associated to Django's Sites framework.
USE_SITES = getattr(settings, "FORMS_BUILDER_USE_SITES",
                    "django.contrib.sites" in settings.INSTALLED_APPS)

# Char to start a quoted choice with.
CHOICES_QUOTE = getattr(settings, "FORMS_BUILDER_CHOICES_QUOTE", "`")

# Char to end a quoted choice with.
CHOICES_UNQUOTE = getattr(settings, "FORMS_BUILDER_CHOICES_UNQUOTE", "`")

# Char to use as a field delimiter when exporting form responses as CSV.
CSV_DELIMITER = getattr(settings, "FORMS_BUILDER_CSV_DELIMITER", ",")
