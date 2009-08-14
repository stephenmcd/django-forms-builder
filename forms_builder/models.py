
from django.db import models
from django.template.defaultfilters import slugify

from forms_builder.settings import UPLOAD_TO


STATUS_DRAFT = 1
STATUS_PUBLIC = 2
STATUS_CHOICES = ((STATUS_DRAFT, "Draft"), (STATUS_PUBLIC, "Public"),)


class BuiltForm(models.Model):
	"""
	a user-built form
	"""

	class Meta:
		verbose_name = "Form"
		verbose_name_plural = "Forms"

	title = models.CharField(max_length=50, unique=True)
	slug = models.SlugField(editable=False, max_length=100, unique=True)
	intro = models.TextField(max_length=2000)
	response = models.TextField(max_length=2000)
	mandatory_extra_fields = models.CharField(max_length=2000)
	optional_extra_fields = models.CharField(max_length=2000)
	status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PUBLIC)
	send_email = models.BooleanField(default=True)
	
	def __unicode__(self):
		return self.title

	def save(self, *args, **kwargs):
		"""
		create a unique slug from title - append an index and increment if it 
		already exists
		"""

		if not self.slug:
			slug = temp = slugify(self.title)
			index = 0
			while True:
				try:
					BuiltForm.objects.get(slug=temp)
				except BuiltForm.DoesNotExist:
					break
				index += 1
				temp = "%s-%s" (slug, index)
			self.slug = temp
		super(BuiltForm, self).save(*args, **kwargs)
		
	@models.permalink
	def get_absolute_url(self):
		return ("built_form_detail", (), {"slug": self.slug})
			
	def extra_fields(self, fields_type):
		fields = getattr(self, "%s_extra_fields" % fields_type).strip("\"")
		if not fields:
			return []
		return eval(fields)


class BuiltFormSubmission(models.Model):
	"""
	a website submission to a user-built form
	"""
	
	class Meta:
		verbose_name = "Form Entry"
		verbose_name_plural = "Form Entries"
	
	built_form = models.ForeignKey(BuiltForm)
	submission_date = models.DateTimeField()

	# mandatory form fields for every form
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.EmailField(max_length=50)
	
	# extra fields for a form that can be user-specified as mandatory or option
	# identified by blank=True
	dob = models.DateField(blank=True, null=True)
	phone = models.CharField(blank=True, max_length=20)
	message = models.TextField(blank=True, max_length=2000)
	image = models.ImageField(blank=True, upload_to=UPLOAD_TO, max_length=50)
	
	def __unicode__(self):
		return "%s Submission: %s %s" % (self.built_form, self.first_name, 
			self.last_name)
		

