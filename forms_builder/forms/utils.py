from __future__ import unicode_literals

from django.template.defaultfilters import slugify as django_slugify
from importlib import import_module
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
    from future.builtins import str
    return django_slugify(unidecode(str(s)))


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


def split_choices(choices_string):
    """
    Convert a comma separated choices string to a list.
    """
    return [x.strip() for x in choices_string.split(",") if x.strip()]


def html5_field(name, base):
    """
    Takes a Django form field class and returns a subclass of
    it with the given name as its input type.
    """
    return type(str(""), (base,), {"input_type": name})


def import_attr(path):
    """
    Given a a Python dotted path to a variable in a module,
    imports the module and returns the variable in it.
    """
    module_path, attr_name = path.rsplit(".", 1)
    return getattr(import_module(module_path), attr_name)
