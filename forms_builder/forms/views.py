# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unidecode import unidecode

import json, unicodedata

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.http import urlquote
from django.views.generic.base import TemplateView
from email_extras.utils import send_mail_template

from forms_builder.forms.forms import FormForForm, EntriesForm
from forms_builder.forms.models import Form, Field, FormEntry, FieldEntry
from forms_builder.forms.settings import USE_SITES, EMAIL_FAIL_SILENTLY
from forms_builder.forms.signals import form_invalid, form_valid
from forms_builder.forms.utils import split_choices


class FormDetail(TemplateView):

    template_name = "forms/form_detail.html"

    def get_context_data(self, **kwargs):
        context = super(FormDetail, self).get_context_data(**kwargs)
        published = Form.objects.published(for_user=self.request.user)
        context["form"] = get_object_or_404(published, slug=kwargs["slug"])
        current_form = Form.objects.get(slug=kwargs["slug"])
        entries_form = EntriesForm(current_form, self.request)

        form_struct = self.make_form_struct(entries_form, context["form"])

        context['form_restrictions'] = json.dumps(form_struct)
        context['form_warnings'] = json.dumps(self.get_warning_messages(form_struct))
        return context

    def make_form_struct(self, entries_form, form):
        form_struct = {}

        fields = Field.objects.filter(form=form)
        for index, field in enumerate(fields):
            if field.max_available:
                form_struct[field.label] = self.get_choices_max(field.choices, field.max_available)
                form_struct[field.label]['field_type'] = field.field_type
                sent_forms = self.get_number_of_sent_entries_for_field_option(entries_form, field, index)
                form_struct[field.label] = self.add_form_struct_with_number_of_sent_forms(form_struct[field.label], sent_forms)
        return form_struct

    @staticmethod
    def get_choices_max(choices_arg, max_available_arg):
        choices = choices_arg.replace(" ", "")
        max_available = max_available_arg.replace(" ", "")
        choices_list = choices.split(",")
        max_available_list = max_available.split(",")
        field_params = {}
        for c, m in zip(choices_list, max_available_list):
            field_params[c] = {'max': m}
        return field_params

    @staticmethod
    def get_number_of_sent_entries_for_field_option(entries_form, field, index):
        choices = field.choices.replace(" ", "").split(',')
        choices_dict = {}
        for choice in choices:
            choices_dict[choice] = 0

        for entry in entries_form.rows():
            entry_choices = entry[index+1].replace(" ", "").split(',')
            for entry_choice in entry_choices:
                choices_dict[entry_choice] += 1
            #TODO: dla kazdego z wyborow osobno trzeba dodac +1 (czyli rozbic to pole do listy i przeiterowac sie po tej liscie)

        return choices_dict

    @staticmethod
    def add_form_struct_with_number_of_sent_forms(form_struct, sent_forms):
        for key, value in sent_forms.items():
            if key in form_struct:
                form_struct[key]['sent'] = value
        return form_struct

    @staticmethod
    def get_warning_messages(form_struct):
        warnings = {}
        for field_name, field_options in form_struct.iteritems():
            warnings[field_name] = []
            for field_option, option_value in field_options.iteritems():
                if isinstance(option_value, dict):
                    if int(option_value['sent']) >= int(option_value['max']):
                        warnings[field_name] += [{field_option:{ 'sent':option_value['sent'], 'max':option_value['max'] }}]
        return warnings

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        login_required = context["form"].login_required
        if login_required and not request.user.is_authenticated():
            path = urlquote(request.get_full_path())
            bits = (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path)
            return redirect("%s?%s=%s" % bits)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        published = Form.objects.published(for_user=request.user)
        form = get_object_or_404(published, slug=kwargs["slug"])
        form_for_form = FormForForm(form, RequestContext(request),
                                    request.POST or None,
                                    request.FILES or None)

        current_form = Form.objects.get(slug=kwargs["slug"])
        entries_form = EntriesForm(current_form, self.request)
        form_struct = self.make_form_struct(entries_form, form)
        query_dict = dict(request.POST.iterlists())
        form_warnings = self.get_warning_messages(form_struct)

        reserve = False
        for question in form_warnings:
            question_decoded = unidecode(question).lower()
            if question_decoded in query_dict:
                for answer in query_dict[question_decoded]:
                    for answer_stats in form_warnings[question]:
                        if answer in answer_stats:
                            reserve = True


        if not form_for_form.is_valid():
            form_invalid.send(sender=request, form=form_for_form)
        else:
            # Attachments read must occur before model save,
            # or seek() will fail on large uploads.
            attachments = []
            for f in form_for_form.files.values():
                f.seek(0)
                attachments.append((f.name, f.read()))
            entry = form_for_form.save(reserved=reserve)
            form_valid.send(sender=request, form=form_for_form, entry=entry)
            self.send_emails(request, form_for_form, form, entry, attachments)
            if not self.request.is_ajax():
                return redirect("form_sent", slug=form.slug)
        context = {"form": form, "form_for_form": form_for_form}
        return self.render_to_response(context)

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax():
            json_context = json.dumps({
                "errors": context["form_for_form"].errors,
                "form": context["form_for_form"].as_p(),
                "message": context["form"].response,
            })
            return HttpResponse(json_context, content_type="application/json")
        return super(FormDetail, self).render_to_response(context, **kwargs)

    def send_emails(self, request, form_for_form, form, entry, attachments):
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
                               fail_silently=EMAIL_FAIL_SILENTLY)
        headers = None
        if email_to:
            headers = {"Reply-To": email_to}
        email_copies = split_choices(form.email_copies)
        if email_copies:
            send_mail_template(subject, "form_response_copies", email_from,
                               email_copies, context=context,
                               attachments=attachments,
                               fail_silently=EMAIL_FAIL_SILENTLY,
                               headers=headers)

form_detail = FormDetail.as_view()


def form_sent(request, slug, template="forms/form_sent.html"):
    """
    Show the response message.
    """
    published = Form.objects.published(for_user=request.user)
    context = {"form": get_object_or_404(published, slug=slug)}
    return render_to_response(template, context, RequestContext(request))
