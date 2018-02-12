from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError

try:
    from django.urls import reverse
except ImportError:
    # For Django 1.8 compatibility
    from django.core.urlresolvers import reverse

from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
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
        authenticated = for_user is not None and for_user.is_authenticated
        if DJANGO_VERSION <= (1, 9):
            # Django 1.8 compatibility, is_authenticated has to be called as a method.
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
        return ("form_detail", (), {"slug": self.slug})

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
        return "<br>".join(links)
    admin_links.allow_tags = True
    admin_links.short_description = ""


class FieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True)


@python_2_unicode_compatible
class AbstractField(models.Model):
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

    def is_a(self, *args):
        """
        Helper that returns True if the field's type is given in any arg.
        """
        return self.field_type in args


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
    form = models.ForeignKey("Form", related_name="entries", on_delete=models.CASCADE)


class FieldEntry(AbstractFieldEntry):
    entry = models.ForeignKey("FormEntry", related_name="fields", on_delete=models.CASCADE)


class Form(AbstractForm):
    pass


class Field(AbstractField):
    """
    Implements automated field ordering.
    """

    form = models.ForeignKey("Form", related_name="fields", on_delete=models.CASCADE)
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
