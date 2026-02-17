# SPDX-PackageName: turku-api
# SPDX-PackageSupplier: Ryan Finnie <ryan@finnie.org>
# SPDX-PackageDownloadLocation: https://github.com/rfinnie/turku-api
# SPDX-FileCopyrightText: © 2015 Canonical Ltd.
# SPDX-FileCopyrightText: © 2015 Ryan Finnie <ryan@finnie.org>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin
from django.views.generic.base import RedirectView

try:
    from django.urls import reverse_lazy  # 1.10+
except ImportError:
    from django.core.urlresolvers import reverse_lazy  # pre-1.10

try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from turku_api import views


admin.autodiscover()

urlpatterns = [
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("admin:index"))),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^v1/", views.urls),
]

try:
    from local_urls import *  # noqa: F401,F403
except ImportError:
    pass
