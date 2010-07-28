
from django import forms
from django.utils.importlib import import_module


class FormForForm(forms.Form):

    def __init__(self, *args, **kwargs):
        form = kwargs.pop("form")
        super(FormForForm, self).__init__(*args, **kwargs)
        for field in form.fields.all():
            if "/" in field.field_type:
                field_class, field_widget = field.field_type.split("/")
            else:
                field_class, field_widget = field.field_type, None
            field_class = getattr(forms, field_class)
            field_args = {"label": field.label, "required": field.required}
            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)
            if field.choices:
                choices = field.choices.split(",")
                field_args["choices"] = zip(choices, choices)
            self.fields["field_%s" % field.id] = field_class(**field_args)
    
