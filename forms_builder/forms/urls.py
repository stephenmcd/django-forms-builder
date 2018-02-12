from __future__ import unicode_literals
try:
    from django.urls import re_path
except ImportError:
    # For Django 1.8 compatibility
    from django.conf.urls import url as re_path

from forms_builder.forms import views


urlpatterns = [
    re_path(r"(?P<slug>.*)/sent/$", views.form_sent, name="form_sent"),
    re_path(r"(?P<slug>.*)/$", views.form_detail, name="form_detail"),
]
