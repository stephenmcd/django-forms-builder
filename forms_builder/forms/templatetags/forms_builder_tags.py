from django import template
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from forms_builder.forms.forms import FormForForm, EntriesForm
from forms_builder.forms.models import Form
import operator


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
            lookup = {
                str(self.name): template.Variable(self.value).resolve(context)
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
        form_args = (form, context, post or None, files or None)
        context["form_for_form"] = FormForForm(*form_args)
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


@register.assignment_tag(takes_context=True)
def form_results(context, form_id, sort_by_cols=None):
    """
    form_results requires the form instance id:

    {% form_results form_instance.id as mytag %}

    results may be sorted by given column number(s):

    {% form_results form_instance.id sort_by_cols="0" as mytag %}
    {% form_results form_instance.id sort_by_cols="3,1" as mytag %}

    """
    request = context['request']
    published = Form.objects.published(for_user=request.user)
    form = get_object_or_404(published, pk=form_id)
    rows = EntriesForm(form, request, None).rows()
    if sort_by_cols:
        cols = [int(c) for c in sort_by_cols.split(',')]
        rows = sorted(rows,
            key=lambda x: ''.join(operator.itemgetter(*cols)(x)).lower())
    return rows
