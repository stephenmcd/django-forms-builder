
from collections import namedtuple

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.test import TestCase

from forms_builder.forms.models import Form, STATUS_DRAFT, STATUS_PUBLISHED
from forms_builder.forms.fields import NAMES
from forms_builder.forms.settings import USE_SITES
from forms_builder.forms.signals import form_invalid, form_valid


current_site = None
if USE_SITES:
    current_site = Site.objects.get_current()


class Tests(TestCase):

    def test_form_fields(self):
        """
        Simple 200 status check against rendering and posting to forms with
        both optional and required fields.
        """
        for required in (True, False):
            form = Form.objects.create(title="Test", status=STATUS_PUBLISHED)
            if USE_SITES:
                form.sites.add(current_site)
                form.save()
            for (field, _) in NAMES:
                form.fields.create(label=field, field_type=field,
                                   required=required, visible=True)
            response = self.client.get(form.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            fields = form.fields.visible()
            data = dict([("field_%s" % f.id, "test") for f in fields])
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
            draft.sites.add(current_site)
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
            form.sites.add(current_site)
            form.save()
        form.fields.create(label="field", field_type=NAMES[0][0],
                           required=True, visible=True)
        self.client.post(form.get_absolute_url(), data={})
        data = {"field_%s" % form.fields.visible()[0].id: "test"}
        self.client.post(form.get_absolute_url(), data=data)
        self.assertEqual(len(events), 0)

    def test_tag(self):
        """
        Test that the different formats for the ``render_built_form``
        tag all work.
        """
        form = Form.objects.create(title="Tags", status=STATUS_PUBLISHED)
        request = namedtuple("Request", ("user",))(user=AnonymousUser())
        context = {"form": form, "request": request}
        template = "{%% load forms_builder_tags %%}{%% render_built_form %s %%}"
        formats = ("form", "form=form", "id=form.id", "slug=form.slug")
        for format in formats:
            t = Template(template % format).render(Context(context))
            self.assertTrue(form.get_absolute_url(), t)


