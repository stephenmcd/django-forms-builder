
from django.conf.urls import *
from views import FormDetail

urlpatterns = patterns("forms_builder.forms.views",
    url(r"(?P<slug>.*)/sent/$", "form_sent", name="form_sent"),
    url(r"(?P<slug>.*)/$", FormDetail.as_view(), name="form_detail"),
)
