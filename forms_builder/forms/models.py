from __future__ import unicode_literals

from django.shortcuts import get_object_or_404

from django.utils import translation

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from django.conf import settings as django_settings

from future.builtins import str

from forms_builder.forms import fields
from forms_builder.forms import settings
from forms_builder.forms.utils import now, slugify, unique_slug


STATUS_DRAFT = 1
STATUS_PUBLISHED = 2
STATUS_CHOICES = (
    (STATUS_DRAFT, _("Draft")),
    (STATUS_PUBLISHED, _("Published")),
)


class FormManager(models.Manager):
    """
    Only show published forms for non-staff users.
    """
    def published(self, for_user=None):
        if for_user is not None and for_user.is_staff:
            return self.all()
        filters = [
            Q(publish_date__lte=now()) | Q(publish_date__isnull=True),
            Q(expiry_date__gte=now()) | Q(expiry_date__isnull=True),
            Q(status=STATUS_PUBLISHED),
        ]
        if settings.USE_SITES:
            filters.append(Q(sites=Site.objects.get_current()))
        return self.filter(*filters)

    def get_or_404(self, slug, language_code, for_user=None):
        published = self.published(for_user=for_user)
        if language_code == django_settings.LANGUAGE_CODE:
            # There are no translations for default language
            return get_object_or_404(published, slug=slug)

        try:
            form_translation = FormTranslationModel.objects.all().get(
                form__in=published,
                language_code=language_code,
                slug=slug,
            )
        except FormTranslationModel.DoesNotExist:
            # Translation doesn't exist, try non-translated:
            return get_object_or_404(published, slug=slug)
        else:
            return form_translation.form



######################################################################
#                                                                    #
#   Each of the models are implemented as abstract to allow for      #
#   subclassing. Default concrete implementations are then defined   #
#   at the end of this module.                                       #
#                                                                    #
######################################################################

@python_2_unicode_compatible
class AbstractForm(models.Model):
    """
    A user-built form.
    """

    sites = models.ManyToManyField(Site,
        default=[settings.SITE_ID], related_name="%(app_label)s_%(class)s_forms")
    title = models.CharField(_("Title"), max_length=50)
    slug = models.SlugField(_("Slug"), editable=settings.EDITABLE_SLUGS,
        max_length=100, unique=True)
    intro = models.TextField(_("Intro"), blank=True)
    button_text = models.CharField(_("Button text"), max_length=50,
        default=_("Submit"))
    response = models.TextField(_("Response"), blank=True)
    redirect_url = models.CharField(_("Redirect url"), max_length=200,
        null=True, blank=True,
        help_text=_("An alternate URL to redirect to after form submission"))
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES,
        default=STATUS_PUBLISHED)
    publish_date = models.DateTimeField(_("Published from"),
        help_text=_("With published selected, won't be shown until this time"),
        blank=True, null=True)
    expiry_date = models.DateTimeField(_("Expires on"),
        help_text=_("With published selected, won't be shown after this time"),
        blank=True, null=True)
    login_required = models.BooleanField(_("Login required"), default=False,
        help_text=_("If checked, only logged in users can view the form"))
    send_email = models.BooleanField(_("Send email"), default=True, help_text=
        _("If checked, the person entering the form will be sent an email"))
    email_from = models.EmailField(_("From address"), blank=True,
        help_text=_("The address the email will be sent from"))
    email_copies = models.CharField(_("Send copies to"), blank=True,
        help_text=_("One or more email addresses, separated by commas"),
        max_length=200)
    email_subject = models.CharField(_("Subject"), max_length=200, blank=True)
    email_message = models.TextField(_("Message"), blank=True)

    objects = FormManager()

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")
        abstract = True

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        """
        Create a unique slug from title - append an index and increment if it
        already exists.
        """
        if not self.slug:
            slug = slugify(self)
            self.slug = unique_slug(self.__class__.objects, "slug", slug)
        super(AbstractForm, self).save(*args, **kwargs)

    def published(self, for_user=None):
        """
        Mimics the queryset logic in ``FormManager.published``, so we
        can check a form is published when it wasn't loaded via the
        queryset's ``published`` method, and is passed to the
        ``render_built_form`` template tag.
        """
        if for_user is not None and for_user.is_staff:
            return True
        status = self.status == STATUS_PUBLISHED
        publish_date = self.publish_date is None or self.publish_date <= now()
        expiry_date = self.expiry_date is None or self.expiry_date >= now()
        authenticated = for_user is not None and for_user.is_authenticated()
        login_required = (not self.login_required or authenticated)
        return status and publish_date and expiry_date and login_required

    def total_entries(self):
        """
        Called by the admin list view where the queryset is annotated
        with the number of entries.
        """
        return self.total_entries
    total_entries.admin_order_field = "total_entries"

    @models.permalink
    def get_absolute_url(self):
        form_translations = self.get_translation()
        if form_translations is not None:
            slug = form_translations.slug or self.slug
        else:
            slug = self.slug

        return ("form_detail", (), {"slug": slug})

    def admin_links(self):
        kw = {"args": (self.id,)}
        links = [
            (_("View form on site"), self.get_absolute_url()),
            (_("Filter entries"), reverse("admin:form_entries", **kw)),
            (_("View all entries"), reverse("admin:form_entries_show", **kw)),
            (_("Export all entries"), reverse("admin:form_entries_export", **kw)),
        ]
        for i, (text, url) in enumerate(links):
            links[i] = "<a href='%s'>%s</a>" % (url, ugettext(text))

        translate_links = []
        for language_code, language_name in django_settings.LANGUAGES:
            if language_code == django_settings.LANGUAGE_CODE:
                # The default language must not be translated ;)
                continue

            # FIXME: NoReverseMatch
            # url = reverse(
            #     "admin:forms_formtranslationmodel_translate",
            #     kwargs={
            #         "form_id" : self.id,
            #         "language_code" : language_code
            #     }
            # )
            url = "/admin/forms/formtranslationmodel/translate/%s/%s/" % (
                self.id, language_code
            )
            translate_links.append(
                '<a href="{url}" title="{name}">{code}</a>'.format(
                    url=url,
                    code=language_code,
                    name=language_name
                )
            )
        links.append(
            "%s %s" % (_("Translate:"), ", ".join(translate_links))
        )
        return "<br>".join(links)
    admin_links.allow_tags = True
    admin_links.short_description = ""

    def get_translation(self, language_code=None):
        """
        returns the corresponding translated FormTranslationModel instance, if exist
        """
        if language_code is None:
            language_code = translation.get_language()

        if language_code == django_settings.LANGUAGE_CODE:
            # The default language must not be translated ;)
            return

        try:
            return FormTranslationModel.objects.all().get(form=self, language_code=language_code)
        except FormTranslationModel.DoesNotExist:
            # not translated, yet
            return None

    def activate_translations(self):
        """
        'Overwrite' field values with translation, if exists.
        So the rendering in template will display the translations.
        """
        form_translations = self.get_translation()
        if form_translations is not None:
            for field in form_translations._meta.get_fields():
                if field.name in ("id", "form", "language_code", "fields"):
                    # Don't change 'internal' fields
                    continue

                # Use translations like 'title', 'slug', 'intro' etc.:
                value = getattr(form_translations, field.name)
                if value:
                    setattr(self, field.name, value)

        return ""  # Don't return None if used by template: {{ form.activate_translations }}


class FieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True)


class CommaSeparatedChoiceMixin:
    """
    used in:
     - AbstractField
     - FieldTranslationModel
    """
    def get_choices(self):
        """
        Parse a comma separated choice string into a list of choices taking
        into account quoted choices using the ``settings.CHOICES_QUOTE`` and
        ``settings.CHOICES_UNQUOTE`` settings.
        """
        choice = ""
        quoted = False
        for char in self.choices:
            if not quoted and char == settings.CHOICES_QUOTE:
                quoted = True
            elif quoted and char == settings.CHOICES_UNQUOTE:
                quoted = False
            elif char == "," and not quoted:
                choice = choice.strip()
                if choice:
                    yield choice, choice
                choice = ""
            else:
                choice += char
        choice = choice.strip()
        if choice:
            yield choice, choice


@python_2_unicode_compatible
class AbstractField(CommaSeparatedChoiceMixin, models.Model):
    """
    A field for a user-built form.
    """

    label = models.CharField(_("Label"), max_length=settings.LABEL_MAX_LENGTH)
    slug = models.SlugField(_('Slug'), max_length=100, blank=True,
            default="")
    field_type = models.IntegerField(_("Type"), choices=fields.NAMES)
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=settings.CHOICES_MAX_LENGTH, blank=True,
        help_text="Comma separated options where applicable. If an option "
            "itself contains commas, surround the option starting with the %s"
            "character and ending with the %s character." %
                (settings.CHOICES_QUOTE, settings.CHOICES_UNQUOTE))
    default = models.CharField(_("Default value"), blank=True,
        max_length=settings.FIELD_MAX_LENGTH)
    placeholder_text = models.CharField(_("Placeholder Text"), null=True,
        blank=True, max_length=100, editable=settings.USE_HTML5)
    help_text = models.CharField(_("Help text"), blank=True, max_length=settings.HELPTEXT_MAX_LENGTH)

    objects = FieldManager()

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        abstract = True

    def __str__(self):
        return str(self.label)

    def is_a(self, *args):
        """
        Helper that returns True if the field's type is given in any arg.
        """
        return self.field_type in args

    def get_translation(self, language_code=None):
        """
        returns the corresponding translated FieldTranslationModel instance, if exist
        """
        if language_code is None:
            language_code = translation.get_language()

        if language_code == django_settings.LANGUAGE_CODE:
            # The default language must not be translated ;)
            return

        try:
            return FieldTranslationModel.objects.get(field=self, language_code=language_code)
        except FieldTranslationModel.DoesNotExist:
            # not translated, yet.
            return None

    def activate_translations(self):
        """
        'Overwrite' field values with translation, if exists.
        So the rendering in template will display the translations.
        """
        field_translations = self.get_translation()
        if field_translations is None:
            # default language is active or not translated, yet.
            return

        for field in field_translations._meta.get_fields():
            if field.name in ("id", "form_translation", "field", "language_code"):
                # Don't change 'internal' fields
                continue

            # Use translations like 'title', 'slug', 'intro' etc.:
            value = getattr(field_translations, field.name)
            if value:
                setattr(self, field.name, value)


class AbstractFormEntry(models.Model):
    """
    An entry submitted via a user-built form.
    """

    entry_time = models.DateTimeField(_("Date/time"))

    class Meta:
        verbose_name = _("Form entry")
        verbose_name_plural = _("Form entries")
        abstract = True


class AbstractFieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a user-built form.
    """

    field_id = models.IntegerField()
    value = models.CharField(max_length=settings.FIELD_MAX_LENGTH,
            null=True)

    class Meta:
        verbose_name = _("Form field entry")
        verbose_name_plural = _("Form field entries")
        abstract = True


###################################################
#                                                 #
#   Default concrete implementations are below.   #
#                                                 #
###################################################

class FormEntry(AbstractFormEntry):
    form = models.ForeignKey("Form", related_name="entries")


class FieldEntry(AbstractFieldEntry):
    entry = models.ForeignKey("FormEntry", related_name="fields")


class Form(AbstractForm):
    pass


class Field(AbstractField):
    """
    Implements automated field ordering.
    """

    form = models.ForeignKey("Form", related_name="fields")
    order = models.IntegerField(_("Order"), null=True, blank=True)

    class Meta(AbstractField.Meta):
        ordering = ("order",)

    def save(self, *args, **kwargs):
        if self.order is None:
            self.order = self.form.fields.count()
        if not self.slug:
            slug = slugify(self).replace('-', '_')
            self.slug = unique_slug(self.form.fields, "slug", slug)
        super(Field, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        fields_after = self.form.fields.filter(order__gte=self.order)
        fields_after.update(order=models.F("order") - 1)
        super(Field, self).delete(*args, **kwargs)


@python_2_unicode_compatible
class FormTranslationModel(models.Model):
    """
    Translations for forms_builder.forms.models.Form

    TODO: validate values with origin form
    e.g.:
        - assert value is emtpy if origin form value is empty
    """
    form = models.ForeignKey(Form, editable=False, related_name="translations",
        on_delete=models.CASCADE
    )
    language_code = models.CharField(_("Language"), editable=False, choices=django_settings.LANGUAGES, max_length=15, db_index=True)

    # Followed fields are the same as in origin Form model, but they are all 'optional':
    # TODO: Create create a base class to merge all double code for Form and FormTranslationModel
    # e.g.: all fields, the "slugify" stuff and get_choices()

    title = models.CharField(_("Title"), max_length=50, null=True, blank=True)
    slug = models.SlugField(_("Slug"), null=True, blank=True, editable=settings.EDITABLE_SLUGS, max_length=100, unique=True)
    intro = models.TextField(_("Intro"), null=True, blank=True)
    button_text = models.CharField(_("Button text"), max_length=50, default=_("Submit"), null=True, blank=True)
    response = models.TextField(_("Response"), null=True, blank=True)
    redirect_url = models.CharField(_("Redirect url"), max_length=200, null=True, blank=True,
        help_text=_("An alternate URL to redirect to after form submission"))

    email_from = models.EmailField(_("From address"), null=True, blank=True,
        help_text=_("The address the email will be sent from"))
    email_copies = models.CharField(_("Send copies to"), null=True, blank=True,
        help_text=_("One or more email addresses, separated by commas"),
        max_length=200)
    email_subject = models.CharField(_("Subject"), max_length=200, null=True, blank=True)
    email_message = models.TextField(_("Message"), null=True, blank=True)

    def __str__(self):
        return "%s (%s: %s)" % (self.form, self.language_code, self.title)

    def save(self, *args, **kwargs):
        """
        Set unique slug from self.title
        """
        if not self.slug and self.title:
            slug = slugify(self.title)
            self.slug = unique_slug(self.__class__.objects, "slug", slug)
        super(FormTranslationModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Form translation")
        verbose_name_plural = _("Form translations")
        unique_together = (
            ("form", "language_code")
        )


@python_2_unicode_compatible
class FieldTranslationModel(CommaSeparatedChoiceMixin, models.Model):
    """
    Translations for forms_builder.forms.models.Field

    TODO: validate values with origin form field
    e.g.:
        - accept choices only if origin is a choice field
        - assert len(choices) == origin len(choices)
    """
    form_translation = models.ForeignKey(
        FormTranslationModel, related_name="fields", editable=False,
        on_delete=models.CASCADE
    )
    field = models.ForeignKey(Field, related_name="translation", editable=False,
        on_delete=models.CASCADE
    )
    language_code = models.CharField(_("Language"), editable=False, choices=django_settings.LANGUAGES, max_length=15, db_index=True)

    # Followed fields are the same as in origin Field model, but they are all 'optional':

    label = models.CharField(_("Label"), null=True, blank=True, max_length=settings.LABEL_MAX_LENGTH)

    choices = models.CharField(_("Choices"), max_length=settings.CHOICES_MAX_LENGTH, null=True, blank=True,
        help_text="Comma separated options where applicable. If an option "
            "itself contains commas, surround the option starting with the %s"
            "character and ending with the %s character." %
                (settings.CHOICES_QUOTE, settings.CHOICES_UNQUOTE))

    default = models.CharField(_("Default value"), null=True, blank=True,
        max_length=settings.FIELD_MAX_LENGTH)

    placeholder_text = models.CharField(_("Placeholder Text"), null=True, blank=True,
        max_length=100, editable=settings.USE_HTML5)

    help_text = models.CharField(_("Help text"), null=True, blank=True,
        max_length=settings.HELPTEXT_MAX_LENGTH)

    def __str__(self):
        return "%s (%s: %s)" % (self.field, self.language_code, self.label)

    class Meta(AbstractField.Meta):
        verbose_name = _("Field translation")
        verbose_name_plural = _("Field translations")
        ordering = (
            "field__order", # use the origin field order
        )
        unique_together = (
            ("field", "language_code")
        )