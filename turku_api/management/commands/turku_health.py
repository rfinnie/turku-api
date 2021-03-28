#!/usr/bin/env python3

# SPDX-PackageSummary: Turku backups - API server
# SPDX-FileCopyrightText: Copyright (C) 2015-2020 Canonical Ltd.
# SPDX-FileCopyrightText: Copyright (C) 2015-2021 Ryan Finnie <ryan@finnie.org>
# SPDX-License-Identifier: AGPL-3.0-or-later

import sys

from django.core.management.base import BaseCommand

from turku_api.models import Machine, Source, Storage


class Command(BaseCommand):
    help = "Report Turku health with a Nagios-compatible check"

    def handle(self, *args, **options):
        storages = Storage.objects.filter(active=True, published=True)
        storages_sick = [o for o in storages if not o.healthy()]
        machines = Machine.objects.filter(active=True, published=True)
        machines_sick = [o for o in machines if not o.healthy()]
        sources = Source.objects.filter(
            machine__active=True, machine__published=True, active=True, published=True
        )
        sources_sick = [o for o in sources if not o.healthy()]
        all_sick = storages_sick + machines_sick + sources_sick

        if all_sick:
            self.stdout.write(
                "CRITICAL {}/{} storages, {}/{} machines, {}/{} sources".format(
                    len(storages_sick),
                    len(storages),
                    len(machines_sick),
                    len(machines),
                    len(sources_sick),
                    len(sources),
                )
            )
            for object in all_sick:
                self.stdout.write(repr(object))
            sys.exit(2)
        else:
            print(
                "OK {} storages, {} machines, {} sources".format(
                    len(storages), len(machines), len(sources)
                )
            )
