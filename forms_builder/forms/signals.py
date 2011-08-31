
from django.dispatch import Signal

form_invalid = Signal(providing_arguments=["form"])
form_valid = Signal(providing_arguments=["form", "entry"])
