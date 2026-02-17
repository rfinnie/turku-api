# SPDX-PackageName: turku-api
# SPDX-PackageSupplier: Ryan Finnie <ryan@finnie.org>
# SPDX-PackageDownloadLocation: https://github.com/rfinnie/turku-api
# SPDX-FileCopyrightText: © 2015 Canonical Ltd.
# SPDX-FileCopyrightText: © 2015 Ryan Finnie <ryan@finnie.org>
# SPDX-License-Identifier: AGPL-3.0-or-later
FROM python:3.12

COPY . /tmp/build
RUN pip install --no-cache-dir '/tmp/build[gunicorn]' && useradd -ms /bin/bash app && rm -rf /tmp/build

ENV DJANGO_SETTINGS_MODULE="turku_api.settings"
USER app
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "-k", "gthread", "--error-logfile", "-", "--capture-output", "turku_api.wsgi:application" ]
EXPOSE 8000/tcp
