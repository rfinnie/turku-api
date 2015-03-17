from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView
from turku_api import views
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    url(r'^v1/health$', views.health, name='health'),
    url(r'^v1/update_config$', views.update_config, name='update_config'),
    url(r'^v1/agent_ping_checkin$', views.agent_ping_checkin, name='agent_ping_checkin'),
    url(r'^v1/storage_ping_checkin$', views.storage_ping_checkin, name='storage_ping_checkin'),
    url(r'^v1/storage_ping_source_update$', views.storage_ping_source_update, name='storage_ping_source_update'),
    url(r'^v1/storage_update_config$', views.storage_update_config, name='storage_update_config'),
    url(r'^admin/', include(admin.site.urls)),
)
