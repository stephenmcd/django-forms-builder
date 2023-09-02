from __future__ import unicode_literals

try:
    from django.urls import include
except ImportError:
    # For Django 1.8 compatibility
    from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import render

from forms_builder.forms.models import Form
from forms_builder.forms import urls as form_urls


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^forms/', include(form_urls)),
    url(r'^$', lambda request: render(request, "index.html",
                                      {"forms": Form.objects.all()})),
]
