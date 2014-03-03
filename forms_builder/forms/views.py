
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.http import urlquote
from email_extras.utils import send_mail_template

from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import Form
from forms_builder.forms.settings import SEND_FROM_SUBMITTER, USE_SITES
from forms_builder.forms.signals import form_invalid, form_valid
from forms_builder.forms.utils import split_choices


def form_detail(request, slug, template="forms/form_detail.html"):
    """
    Display a built form and handle submission.
    """
    published = Form.objects.published(for_user=request.user)
    form = get_object_or_404(published, slug=slug)
    if form.login_required and not request.user.is_authenticated():
        return redirect("%s?%s=%s" % (settings.LOGIN_URL, REDIRECT_FIELD_NAME,
                        urlquote(request.get_full_path())))
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
            context = {
                "fields": fields,
                "message": form.email_message,
                "request": request,
            }
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
            return redirect(reverse("form_sent", kwargs={"slug": form.slug}))
    context = {"form": form}
    return render_to_response(template, context, request_context)


def form_sent(request, slug, template="forms/form_sent.html"):
    """
    Show the response message.
    """
    published = Form.objects.published(for_user=request.user)
    form = get_object_or_404(published, slug=slug)
    context = {"form": form}
    return render_to_response(template, context, RequestContext(request))
