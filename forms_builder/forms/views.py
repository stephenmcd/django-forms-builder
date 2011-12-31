
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.http import urlquote

from forms_builder.forms.models import Form


def form_detail(request, slug, template="forms/form_detail.html"):
    """
    Display a built form and handle submission.
    """
    try:
        form = Form.objects.get_form_for_request(request, slug)
    except Form.DoesNotExist:
        raise Http404
    except Form.objects.LoginRequired:
        return redirect("%s?%s=%s" % (settings.LOGIN_URL, REDIRECT_FIELD_NAME,
                        urlquote(request.get_full_path())))
    if request.method == "POST":
        entry, form_for_form = form.process_form(request)
        if entry:
            return redirect(reverse("form_sent", kwargs={"slug": form.slug}))
    else:
        form_for_form = form.form_for_form()
    context = {"form": form, "form_for_form": form_for_form}
    return render_to_response(template, context, RequestContext(request))

def form_sent(request, slug, template="forms/form_sent.html"):
    """
    Show the response message.
    """
    try:
        form = Form.objects.get_form_for_request(request, slug)
    except Form.DoesNotExist:
        raise Http404
    except Form.objects.LoginRequired:
        return redirect("%s?%s=%s" % (settings.LOGIN_URL, REDIRECT_FIELD_NAME,
                        urlquote(request.get_full_path())))
    context = {"form": form}
    return render_to_response(template, context, RequestContext(request))
