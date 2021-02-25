from __future__ import unicode_literals

from django.urls import re_path, include
from django.contrib import admin
from django.shortcuts import render

from forms_builder.forms.models import Form
from forms_builder.forms import urls as form_urls


admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^forms/', include(form_urls)),
    re_path(r'^$', lambda request: render(request, "index.html",
                                      {"forms": Form.objects.all()})),
]
