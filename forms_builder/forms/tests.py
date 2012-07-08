from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.template import Context, RequestContext, Template
from django.test import TestCase

from forms_builder.forms.models import (Form, Field,
                                        STATUS_DRAFT, STATUS_PUBLISHED)
from forms_builder.forms.fields import NAMES, FILE
from forms_builder.forms.settings import USE_SITES
from forms_builder.forms.signals import form_invalid, form_valid
from forms_builder.forms.forms import FormForForm


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
        request = type("Request", (), {"META": {}, "user": AnonymousUser()})()
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
        #should not raise IntegrityError: forms_fieldentry.value may not be NULL
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
        form = Form.objects.create(title="Test")
        if USE_SITES:
            form.sites.add(self._site)
            form.save()
        form.fields.create(label="field", field_type=NAMES[0][0],
                           required=True, visible=True)
        response = self.client.post(form.get_absolute_url(), {"foo": "bar"})
        self.assertTrue("This field is required" in response.content)
