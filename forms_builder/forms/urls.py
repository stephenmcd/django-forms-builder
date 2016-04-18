from __future__ import unicode_literals

from django.conf.urls import url

from forms_builder.forms import views


urlpatterns = [
    url(r"(?P<slug>.*)/sent/$", views.form_sent, name="form_sent"),
    url(r"(?P<slug>.*)/$", views.form_detail, name="form_detail"),
]
