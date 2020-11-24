# Turku backups - API server
# Copyright (C) 2015-2020 Canonical Ltd., Ryan Finnie and other contributors
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

from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import RedirectView

try:
    from django.urls import reverse_lazy  # 1.10+
except ImportError:
    from django.core.urlresolvers import reverse_lazy  # pre-1.10

from turku_api import views


admin.autodiscover()

urlpatterns = [
    url(r"^$", RedirectView.as_view(url=reverse_lazy("admin:index"))),
    url(r"^admin/", admin.site.urls),
]
for view_name in views.ViewV1.view_names:
    urlpatterns.append(
        url(r"^v1/{}$".format(view_name), views.view_handler, name=view_name)
    )

try:
    from local_urls import *  # noqa: F401,F403
except ImportError:
    pass
