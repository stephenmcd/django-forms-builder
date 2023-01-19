from django.dispatch import Signal

form_invalid = Signal(["form"])
form_valid = Signal(["form", "entry"])
