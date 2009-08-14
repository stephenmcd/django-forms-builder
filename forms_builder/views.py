
from datetime import datetime
from os.path import join

from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from forms_builder.models import BuiltForm, BuiltFormSubmission
from forms_builder.utils import get_built_form
from forms_builder.forms import get_built_form_form
from forms_builder.settings import UPLOAD_TO, EMAIL_TO


def built_form_detail(request, slug, 
	template="forms_builder/built_form_detail.html"):
	"""
	display a built form and handle submission
	"""
	
	built_form = get_built_form(request, slug)

	if request.method == "POST":
		
		built_form_form = get_built_form_form(built_form)(
			request.POST, request.FILES)
		if built_form_form.is_valid():
			
			# add the form and date to the submmission data
			built_form_form.cleaned_data.update({"submission_date": 
				datetime.now(), "built_form_id": built_form.id})
					
			# create the submission and save any files
			attachments = []
			submission = BuiltFormSubmission(**built_form_form.cleaned_data)
			for name, file in built_form_form.files.items():
				filename = default_storage.save("%s/%s" % (UPLOAD_TO, 
					file.name), file)
				setattr(submission, name, filename)
				attachments.append(filename)
			submission.save()

			# send email if specified
			fields = []
			if built_form.send_email and EMAIL_TO:
				for field in submission._meta.fields:
					value = getattr(submission, field.name)
					if value:
						fields.append("%s: %s" % (field.verbose_name, value))
				msg = EmailMessage(submission, "\n".join(fields), 
					submission.email, [EMAIL_TO])
				for attachment in attachments:
					msg.attach_file(join(default_storage.location, attachment))
				msg.send(fail_silently=False)

			return HttpResponseRedirect(reverse("built_form_sent", 
				kwargs={"slug": built_form.slug}))
					
	else:
		
		# pre-populate relevant fields if user is logged in
		initial = {}
		if request.user.is_authenticated():
			initial = {"first_name": request.user.first_name, "last_name": 
				request.user.last_name, "email": request.user.email}
		built_form_form = get_built_form_form(built_form)(initial=initial)
		
	return render_to_response(template, {"built_form": built_form, 
		"built_form_form": built_form_form}, RequestContext(request))


def built_form_sent(request, slug, 
	template="forms_builder/built_form_sent.html"):
	"""
	show the response message
	"""

	return render_to_response(template, {"built_form": 
		get_built_form(request, slug)}, RequestContext(request))
