from __future__ import unicode_literals

from django.utils import translation

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.template import Context, RequestContext, Template
from django.test import TestCase

from forms_builder.forms.fields import NAMES, FILE
from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import (Form, Field,
    STATUS_DRAFT, STATUS_PUBLISHED, FormTranslationModel, FieldTranslationModel)
from forms_builder.forms.settings import USE_SITES
from forms_builder.forms.signals import form_invalid, form_valid


class Tests(TestCase):

    def setUp(self):
        self._site = Site.objects.get_current()

    def test_form_fields(self):
        """
        Simple 200 status check against rendering and posting to forms with
        both optional and required fields.
        """
        for required in (True, False):
            form = Form.objects.create(title="Test", status=STATUS_PUBLISHED)
            if USE_SITES:
                form.sites.add(self._site)
                form.save()
            for (field, _) in NAMES:
                form.fields.create(label=field, field_type=field,
                                   required=required, visible=True)
            response = self.client.get(form.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            fields = form.fields.visible()
            data = dict([(f.slug, "test") for f in fields])
            response = self.client.post(form.get_absolute_url(), data=data)
            self.assertEqual(response.status_code, 200)

    def test_draft_form(self):
        """
        Test that a form with draft status is only visible to staff.
        """
        settings.DEBUG = True # Don't depend on having a 404 template.
        username = "test"
        password = "test"
        User.objects.create_superuser(username, "", password)
        self.client.logout()
        draft = Form.objects.create(title="Draft", status=STATUS_DRAFT)
        if USE_SITES:
            draft.sites.add(self._site)
            draft.save()
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        self.client.login(username=username, password=password)
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_form_signals(self):
        """
        Test that each of the signals are sent.
        """
        events = ["valid", "invalid"]
        invalid = lambda **kwargs: events.remove("invalid")
        form_invalid.connect(invalid)
        valid = lambda **kwargs: events.remove("valid")
        form_valid.connect(valid)
        form = Form.objects.create(title="Signals", status=STATUS_PUBLISHED)
        if USE_SITES:
            form.sites.add(self._site)
            form.save()
        form.fields.create(label="field", field_type=NAMES[0][0],
                           required=True, visible=True)
        self.client.post(form.get_absolute_url(), data={})
        data = {form.fields.visible()[0].slug: "test"}
        self.client.post(form.get_absolute_url(), data=data)
        self.assertEqual(len(events), 0)

    def test_tag(self):
        """
        Test that the different formats for the ``render_built_form``
        tag all work.
        """
        form = Form.objects.create(title="Tags", status=STATUS_PUBLISHED)
        request = type(str(""), (), {"META": {}, "user": AnonymousUser()})()
        context = RequestContext(request, {"form": form})
        template = "{%% load forms_builder_tags %%}{%% render_built_form %s %%}"
        formats = ("form", "form=form", "id=form.id", "slug=form.slug")
        for format in formats:
            t = Template(template % format).render(context)
            self.assertTrue(form.get_absolute_url(), t)

    def test_optional_filefield(self):
        form = Form.objects.create(title="Test", status=STATUS_PUBLISHED)
        if USE_SITES:
            form.sites.add(self._site)
        form.save()
        form.fields.create(label="file field",
                field_type=FILE,
                required=False,
                visible=True)
        fields = form.fields.visible()
        data = {'field_%s' % fields[0].id: ''}
        context = Context({})
        form_for_form = FormForForm(form, context, data=data)
        # Should not raise IntegrityError: forms_fieldentry.value
        # may not be NULL
        form_for_form.save()


    def test_field_validate_slug_names(self):
        form = Form.objects.create(title="Test")
        field = Field(form=form,
                label="First name", field_type=NAMES[0][0])
        field.save()
        self.assertEqual(field.slug, 'first_name')

        field_2 = Field(form=form,
                label="First name", field_type=NAMES[0][0])
        try:
            field_2.save()
        except IntegrityError:
            self.fail("Slugs were not auto-unique")

    def test_field_default_ordering(self):
        form = Form.objects.create(title="Test")
        form.fields.create(label="second field",
                field_type=NAMES[0][0], order=2)
        f1 = form.fields.create(label="first field",
                field_type=NAMES[0][0], order=1)
        self.assertEqual(form.fields.all()[0], f1)

    def test_form_errors(self):
        from future.builtins import str
        form = Form.objects.create(title="Test")
        if USE_SITES:
            form.sites.add(self._site)
            form.save()
        form.fields.create(label="field", field_type=NAMES[0][0],
                           required=True, visible=True)
        response = self.client.post(form.get_absolute_url(), {"foo": "bar"})
        self.assertTrue("This field is required" in str(response.content))

    def test_form_redirect(self):
        redirect_url = 'http://example.com/foo'
        form = Form.objects.create(title='Test', redirect_url=redirect_url)
        if USE_SITES:
            form.sites.add(self._site)
            form.save()
        form.fields.create(label='field', field_type=NAMES[3][0],
                           required=True, visible=True)
        form_absolute_url = form.get_absolute_url()
        response = self.client.post(form_absolute_url, {'field': '0'})
        self.assertEqual(response["location"], redirect_url)
        response = self.client.post(form_absolute_url, {'field': 'bar'})
        self.assertFalse(isinstance(response, HttpResponseRedirect))

    def test_translation(self):
        form = Form.objects.create(title='The title in English.', status=STATUS_PUBLISHED)
        if USE_SITES:
            form.sites.add(self._site)
            form.save()

        f1 = form.fields.create(label="field no. 1 in English",
            field_type=NAMES[0][0], # "Single line text"
            order=1
        )
        f2 = form.fields.create(label="field no. 2 in English",
            field_type=NAMES[0][0], # "Single line text"
            order=2
        )
        form_translation = FormTranslationModel.objects.create(
            form=form,
            language_code="de",
            title="Der Titel in Deutsch."
        )
        FieldTranslationModel.objects.create(
            form_translation = form_translation,
            field=f1,
            language_code="de",
            label="Feld Nr. 1 in Deutsch"
        )
        FieldTranslationModel.objects.create(
            form_translation = form_translation,
            field=f2,
            language_code="de",
            label="Feld Nr. 2 in Deutsch"
        )


        # request and assert form in english:

        with translation.override("en"):
            form_absolute_url_en = form.get_absolute_url()

        self.assertEqual(form_absolute_url_en, "/en/forms/the-title-in-english/")

        response = self.client.get(form_absolute_url_en, HTTP_ACCEPT_LANGUAGE="en")
        content = response.content.decode("utf-8")
        # print(content)
        self.assertEqual(response.status_code, 200)

        self.assertInHTML('<h1>The title in English.</h1>', content)
        self.assertInHTML('<label for="id_field_no_1_in_english">field no. 1 in English:</label>', content)
        self.assertInHTML('<label for="id_field_no_2_in_english">field no. 2 in English:</label>', content)


        # request and assert form in german:

        with translation.override("de"):
            form_absolute_url_de = form.get_absolute_url()

        self.assertEqual(form_absolute_url_de, "/de/forms/the-title-in-english/") # FIXME: Should we translate url, too?

        response = self.client.get(form_absolute_url_de, HTTP_ACCEPT_LANGUAGE="de")
        content = response.content.decode("utf-8")
        # print(content)
        self.assertEqual(response.status_code, 200)

        self.assertInHTML('<h1>Der Titel in Deutsch.</h1>', content)
        self.assertInHTML('<label for="id_field_no_1_in_english">Feld Nr. 1 in Deutsch:</label>', content)
        self.assertInHTML('<label for="id_field_no_2_in_english">Feld Nr. 2 in Deutsch:</label>', content)