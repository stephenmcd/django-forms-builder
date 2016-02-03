from __future__ import unicode_literals

from django.conf.urls import patterns, url
from .views import form_sent, form_detail

urlpatterns = [
    url(r"(?P<slug>.*)/sent/$", form_sent, name="form_sent"),
    url(r"(?P<slug>.*)/$", form_detail, name="form_detail"),
]
