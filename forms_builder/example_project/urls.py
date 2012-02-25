from django.conf.urls.defaults import patterns, include, url
import forms_builder.forms.urls # add this import

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^forms/', include(forms_builder.forms.urls)),
)
