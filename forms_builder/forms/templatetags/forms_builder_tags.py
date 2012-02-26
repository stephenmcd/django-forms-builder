
from django import template
from django.template.loader import get_template

from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import Form


register = template.Library()


class BuiltFormNode(template.Node):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self, context):
        user = context["request"].user
        if self.name != "form":
            lookup = {
                self.name: template.Variable(self.value).resolve(context)
            }
            try:
                form = Form.objects.published(for_user=user).get(**lookup)
            except Form.DoesNotExist:
                form = None
        else:
            form = template.Variable(self.value).resolve(context)
        if not isinstance(form, Form) or (form.login_required and not
                                          user.is_authenticated()):
            return ""
        t = get_template("forms/includes/built_form.html")
        context["form"] = form
        context["form_for_form"] = FormForForm(form)
        return t.render(context)


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
