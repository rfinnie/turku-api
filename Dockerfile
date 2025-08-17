# SPDX-PackageSummary: Turku backups - API server
# SPDX-FileCopyrightText: Copyright (C) 2015-2020 Canonical Ltd.
# SPDX-FileCopyrightText: Copyright (C) 2015-2025 Ryan Finnie <ryan@finnie.org>
# SPDX-License-Identifier: AGPL-3.0-or-later
FROM python:3.12

COPY . /tmp/build
RUN pip install --no-cache-dir '/tmp/build[gunicorn]' && useradd -ms /bin/bash app && rm -rf /tmp/build

ENV DJANGO_SETTINGS_MODULE="turku_api.settings"
USER app
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "-k", "gthread", "--error-logfile", "-", "--capture-output", "turku_api.wsgi:application" ]
EXPOSE 8000/tcp
