
from datetime import datetime

from django import forms
from django.utils.importlib import import_module

from forms_builder.forms.models import FormEntry, FIELD_MAX_LENGTH


class FormForForm(forms.ModelForm):

    class Meta:
        model = FormEntry
        exclude = ("form", "entry_time")

    def __init__(self, form, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model 
        instance and its related field model instances.
        """
        self._form = form
        self._formfields = form.fields.filter(visible=True)
        super(FormForForm, self).__init__(*args, **kwargs)
        for field in self._formfields:
            if "/" in field.field_type:
                field_class, field_widget = field.field_type.split("/")
            else:
                field_class, field_widget = field.field_type, None
            field_class = getattr(forms, field_class)
            field_args = {"label": field.label, "required": field.required, 
                "max_length": FIELD_MAX_LENGTH}
            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)
            if field.choices:
                choices = field.choices.split(",")
                field_args["choices"] = zip(choices, choices)
            self.fields["field_%s" % field.id] = field_class(**field_args)

    def save(self, **kwargs):
        """
        Create a FormEntry instance.
        """
        entry = super(FormForForm, self).save(commit=False)
        entry.form = self._form
        entry.entry_time = datetime.now()
        entry.save()
        for field in self._formfields:
            entry.fields.create(field_id=field.id, 
                value=self.cleaned_data["field_%s" % field.id])
        return entry
