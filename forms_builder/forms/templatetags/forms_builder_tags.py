from __future__ import unicode_literals
from future.builtins import str

from django import template
from django.template.loader import get_template

from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import Form, AbstractForm


register = template.Library()


class BuiltFormNode(template.Node):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self, context):
        request = context["request"]
        user = getattr(request, "user", None)
        post = getattr(request, "POST", None)
        files = getattr(request, "FILES", None)
        if self.name != "form":
            lookup_value = template.Variable(self.value).resolve(context)
            try:
                form = Form.objects.get(**{str(self.name): lookup_value})
            except Form.DoesNotExist:
                form = None
        else:
            form = template.Variable(self.value).resolve(context)
        if (not issubclass(form.__class__, AbstractForm)
                or not form.published(for_user=user)):
            return ""
        t = get_template("forms/includes/built_form.html")
        context["form"] = form
        form_args = (form, context, post or None, files or None)
        context["form_for_form"] = FormForForm(*form_args)
        return t.render(context.flatten())


@register.tag
def render_built_form(parser, token):
    """
    render_build_form takes one argument in one of the following formats:

    {% render_build_form form_instance %}
    {% render_build_form form=form_instance %}
    {% render_build_form id=form_instance.id %}
    {% render_build_form slug=form_instance.slug %}

    """
    try:
        _, arg = token.split_contents()
        if "=" not in arg:
            arg = "form=" + arg
        name, value = arg.split("=", 1)
        if name not in ("form", "id", "slug"):
            raise ValueError
    except ValueError:
        e = ()
        raise template.TemplateSyntaxError(render_built_form.__doc__)
    return BuiltFormNode(name, value)
