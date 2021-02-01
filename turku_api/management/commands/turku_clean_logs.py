#!/usr/bin/env python3

# Turku backups
# Copyright (C) 2015-2020 Canonical Ltd., Ryan Finnie and other contributors
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from turku_api.models import BackupLog


class Command(BaseCommand):
    help = "Turku clean logs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            required=True,
            help="Clean logs older than this number of days",
        )

    def handle(self, *args, **options):
        for backuplog in BackupLog.objects.filter(
            date_end__lt=(timezone.now() - datetime.timedelta(days=options["days"]))
        ):
            backuplog.delete()
