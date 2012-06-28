from django.template.defaultfilters import slugify as generic_slugify

def slugify(input_text):
    try:
        from unidecode import unidecode
        slug = generic_slugify(unidecode(input_text))
    except ImportError:
        slug = generic_slugify(input_text)
    return slug
