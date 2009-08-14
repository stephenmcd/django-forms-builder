

from django.conf.urls.defaults import patterns, url
from forms_builder.views import built_form_detail, built_form_sent

urlpatterns = patterns("",
    url(r'(?P<slug>.*)/sent/$', built_form_sent, name="built_form_sent"),
    url(r'(?P<slug>.*)/$', built_form_detail, name="built_form_detail"),
)


