from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from forms_builder.forms.models import Form
import forms_builder.forms.urls # add this import

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^forms/', include(forms_builder.forms.urls)),
    url(r'^$', direct_to_template, {
        "template": "index.html",
        "extra_context": {"forms": lambda: Form.objects.all()},
    }),
)
