
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
        self.form = form
        self.form_fields = form.fields.filter(visible=True)
        self.field_values = []
        self.email_field = None
        super(FormForForm, self).__init__(*args, **kwargs)
        for field in self.form_fields:
            field_key = "field_%s" % field.id
            if "/" in field.field_type:
                field_class, field_widget = field.field_type.split("/")
            else:
                field_class, field_widget = field.field_type, None
            if self.email_field is None and field_class == "EmailField":
                self.email_field = field_key
            field_class = getattr(forms, field_class)
            field_args = {"label": field.label, "required": field.required}
            arg_names = field_class.__init__.im_func.func_code.co_varnames
            if "max_length" in arg_names:
                field_args["max_length"] = FIELD_MAX_LENGTH
            if "choices" in arg_names:
                choices = field.choices.split(",")
                field_args["choices"] = zip(choices, choices)
            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)
            self.fields[field_key] = field_class(**field_args)

    def save(self, **kwargs):
        """
        Create a FormEntry instance and related FieldEntry instances for each 
        form field.
        """
        entry = super(FormForForm, self).save(commit=False)
        entry.form = self.form
        entry.entry_time = datetime.now()
        entry.save()
        self.field_values = []
        for field in self.form_fields:
            value = self.cleaned_data["field_%s" % field.id]
            field = entry.fields.create(field_id=field.id, label=field.label, 
                value=value)
            print field
            self.field_values.append(field)
        return entry
        
    def email_to(self):
        """
        Return the value entered for the first field of type EmailField.
        """
        if self.email_field is None:
            return None
        return self.cleaned_data.get("field_%s" % self.email_field)
        
