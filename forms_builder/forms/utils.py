
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


def unique_slug(manager, slug_field, slug):
    """
    Ensure slug is unique for the given manager, appending a digit
    if it isn't.
    """
    i = 0
    while True:
        if i > 0:
            if i > 1:
                slug = slug.rsplit("-", 1)[0]
            slug = "%s-%s" % (slug, i)
        if not manager.filter(**{slug_field: slug}):
            break
        i += 1
    return slug

