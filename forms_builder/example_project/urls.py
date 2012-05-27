
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from forms_builder.forms.models import Form
from forms_builder.forms import urls as form_urls


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^forms/', include(form_urls)),
    url(r'^$', lambda request: TemplateView.as_view(
        template_name="index.html")(request, forms=Form.objects.all())),
)
