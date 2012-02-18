from django.template import Context
from django.template.base import Variable
from django.template.loader import get_template
from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()

# The tag genarates a context variable containing a bound form
# {% bound_form_for p.fields.form as f %}.</p>

@register.tag('bound_form_for')
def bound_form_for(parser, token):
    try:
        tag_name, form_object_variable, as_, varname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Wrong syntax for the %r tag" % token.contents.split()[0])
    if as_ != 'as':
        raise template.TemplateSyntaxError("Wrong syntax for the %r tag" % token.contents.split()[0])
    return FormRenderingNode(form_object_variable, varname)

class FormRenderingNode(template.Node):
    def __init__(self, form_object_variable, varname):
        self.form_object_variable = form_object_variable
        self.varname = varname

    def render(self, context):
        request = context.get('request')
        if request:
            form_object = Variable(self.form_object_variable).resolve(context)
            if request.method == "GET":
                form = form_object.empty_form()
            elif request.method == "POST":
                form_object.process_form(request)
                form = form_object.bound_form
        else:
            form = None
        context[self.varname] = form
        return ''
