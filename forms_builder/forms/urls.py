from django.conf.urls.defaults import *

urlpatterns = patterns("forms_builder.forms.views",
    url(r"(?P<slug>.*)/$", "form_detail", name="form_detail"),
)
