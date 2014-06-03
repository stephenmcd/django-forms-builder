from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from email_extras.utils import send_mail_template

from forms_builder.forms.models import Form
from forms_builder.forms.forms import FormForForm
from forms_builder.forms.signals import form_invalid, form_valid
from forms_builder.forms.utils import split_choices
from forms_builder.contrib.cms.models import Forms


class FormPlugin(CMSPluginBase):
    module = _("Forms")
    model = Forms
    name = _("Form")
    render_template = "forms/cms/form_detail.html"
    text_enabled = True
    allow_children = False
    cache = False

    def render(self, context, instance, placeholder):
        """
        Display a built form and handle submission.
        """
        request = context['request']
        slug = instance.form.slug

        published = Form.objects.published(for_user=request.user)
        form = get_object_or_404(published, slug=slug)
        if form.login_required and not request.user.is_authenticated():
            self.render_template = "forms/cms/not_allowed.html"
            return context
        request_context = RequestContext(request)
        args = (form, request_context, request.POST or None, request.FILES or None)
        form_for_form = FormForForm(*args)
        if request.method == "POST":
            if not form_for_form.is_valid():
                form_invalid.send(sender=request, form=form_for_form)
            else:
                entry = form_for_form.save()
                subject = form.email_subject
                if not subject:
                    subject = "%s - %s" % (form.title, entry.entry_time)
                fields = []
                for (k, v) in form_for_form.fields.items():
                    value = form_for_form.cleaned_data[k]
                    if isinstance(value, list):
                        value = ", ".join([i.strip() for i in value])
                    fields.append((v.label, value))
                context.update({
                    "fields": fields,
                    "message": form.email_message,
                    "request": request,
                })
                email_from = form.email_from or settings.DEFAULT_FROM_EMAIL
                email_to = form_for_form.email_to()
                if email_to and form.send_email:
                    send_mail_template(subject, "form_response", email_from,
                                       email_to, context=context,
                                       fail_silently=settings.DEBUG)
                headers = None
                if email_to:
                    # Add the email entered as a Reply-To header
                    headers = {'Reply-To': email_to}
                email_copies = split_choices(form.email_copies)
                if email_copies:
                    attachments = []
                    for f in form_for_form.files.values():
                        f.seek(0)
                        attachments.append((f.name, f.read()))
                    send_mail_template(subject, "form_response", email_from,
                                       email_copies, context=context,
                                       attachments=attachments,
                                       fail_silently=settings.DEBUG,
                                       headers=headers)
                form_valid.send(sender=request, form=form_for_form, entry=entry)
                self.render_template = "forms/cms/form_sent.html"
        context.update({
            'form': form,
        })
        return context

plugin_pool.register_plugin(FormPlugin)
