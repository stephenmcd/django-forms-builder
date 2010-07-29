
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import Form
from forms_builder.forms.utils import get_form


def form_detail(request, slug, template="forms/form_detail.html"):
    """
    Display a built form and handle submission.
    """    
    form = get_form(request, slug)
    form_for_form = FormForForm(form, request.POST or None)
    if request.method == "POST":
        if form_for_form.is_valid():
            entry = form_for_form.save()
            fields = "\n".join([unicode(f) for f in form_for_form.field_values])
            email_from = form.email_from or settings.DEFAULT_FROM_EMAIL
            email_to = form_for_form.email_to()
            if email_to and form.send_email:
                msg = EmailMessage(entry, fields, email_from, [email_to])
                msg.send()
            email_copies = form.email_copies.split(",")
            email_copies = filter(None, [e.strip() for e in email_copies])
            email_from = email_to or email_from # Send from the email entered.
            if email_copies:
                msg = EmailMessage(entry, fields, email_from, email_copies)
                msg.send()
            return redirect(reverse("form_sent", kwargs={"slug": form.slug}))
    context = {"form": form, "form_for_form": form_for_form}
    return render_to_response(template, context, RequestContext(request))

def form_sent(request, slug, template="forms/form_sent.html"):
    """
    Show the response message.
    """
    context = {"form": get_form(request, slug)}
    return render_to_response(template, context, RequestContext(request))
