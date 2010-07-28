
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


STATUS_DRAFT = 1
STATUS_PUBLIC = 2
STATUS_CHOICES = (
    (STATUS_DRAFT, "Draft"), 
    (STATUS_PUBLIC, "Public"),
)

FIELD_CHOICES = (
    ("CharField", _("Single line text")),
    ("CharField/django.forms.Textarea", _("Multi line text")),
    ("EmailField", _("Email")),
    ("BooleanField", _("Check box")),
    ("ChoiceField", _("Drop down")),
    ("MultipleChoiceField", _("Multi select")),
    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
    ("DateTimeField", _("Date/time")),
)

class Form(models.Model):
    """
    A user-built form.
    """

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")

    title = models.CharField(_("Title"), max_length=50, unique=True)
    slug = models.SlugField(editable=False, max_length=100, unique=True)
    intro = models.TextField(_("Intro"), max_length=2000)
    response = models.TextField(_("Response"), max_length=2000)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, 
        default=STATUS_PUBLIC)
    send_email = models.BooleanField(_("Send email response"), default=True)
    send_copy = models.CharField(_("Send copies to"), max_length=200, 
        help_text=_("One or more email addresses, separated by commas"), 
        blank=True)
    
    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Create a unique slug from title - append an index and increment if it 
        already exists.
        """

        if not self.slug:
            slug = temp = slugify(self.title)
            index = 0
            while True:
                try:
                    Form.objects.get(slug=temp)
                except Form.DoesNotExist:
                    break
                index += 1
                temp = "%s-%s" (slug, index)
            self.slug = temp
        super(Form, self).save(*args, **kwargs)
        
    @models.permalink
    def get_absolute_url(self):
        return ("form_detail", (), {"slug": self.slug})

class Field(models.Model):
    """
    A field for a user-built form.
    """
    
    form = models.ForeignKey("Form", related_name="fields")
    label = models.CharField(_("Label"), max_length=20)
    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES, 
        max_length=50)
    required = models.BooleanField(_("Required"), default=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
        help_text="Comma separated options where applicable")

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        order_with_respect_to = "form"
    
    def __unicode__(self):
        return self.label
