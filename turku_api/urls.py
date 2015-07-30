# Turku backups - API server
# Copyright 2015 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the Affero GNU General Public License for more details.
#
# You should have received a copy of the Affero GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

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
    url(r'^v1/agent_ping_restore$', views.agent_ping_restore, name='agent_ping_restore'),
    url(r'^v1/storage_ping_checkin$', views.storage_ping_checkin, name='storage_ping_checkin'),
    url(r'^v1/storage_ping_source_update$', views.storage_ping_source_update, name='storage_ping_source_update'),
    url(r'^v1/storage_update_config$', views.storage_update_config, name='storage_update_config'),
    url(r'^admin/', include(admin.site.urls)),
)

try:
    from local_urls import *
except ImportError:
    pass
