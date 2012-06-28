
from django.template.defaultfilters import slugify as django_slugify
from unidecode import unidecode


# Timezone support with fallback.
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now


def slugify(s):
    """
    Translates unicode into closest possible ascii chars before
    slugifying.
    """
    return django_slugify(unidecode(unicode(s)))
