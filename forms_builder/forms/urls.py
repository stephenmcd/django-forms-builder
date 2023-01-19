from django.urls import re_path
from forms_builder.forms import views


urlpatterns = [
    re_path(r"(?P<slug>.*)/sent/$", views.form_sent, name="form_sent"),
    re_path(r"(?P<slug>.*)/$", views.form_detail, name="form_detail"),
]
