
from datetime import datetime
from os.path import join

from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import Form
from forms_builder.forms.utils import get_form
from forms_builder.forms.settings import UPLOAD_TO, EMAIL_TO


def form_detail(request, slug, template="forms/form_detail.html"):
    """
    Display a built form and handle submission.
    """
    
    form = get_form(request, slug)
    form_for_form = FormForForm(form, request.POST or None)

    if request.method == "POST":
        if form_for_form.is_valid():
            form_for_form.save()
            return redirect(reverse("form_sent", kwargs={"slug": form.slug}))

    context = {"form": form, "form_for_form": form_for_form}
    return render_to_response(template, context, RequestContext(request))

def form_sent(request, slug, template="forms/form_sent.html"):
    """
    Show the response message.
    """
    context = {"form": get_form(request, slug)}
    return render_to_response(template, context, RequestContext(request))
