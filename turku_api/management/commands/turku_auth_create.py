#!/usr/bin/env python3

# Turku backups
# Copyright (C) 2015-2020 Canonical Ltd., Ryan Finnie and other contributors
#
# SPDX-License-Identifer: AGPL-3.0-or-later

from django.contrib.auth import hashers
from django.core.management.base import BaseCommand

from turku_api.models import Auth


class Command(BaseCommand):
    help = "Turku Auth secret creation"

    def add_arguments(self, parser):
        parser.add_argument(
            "secret_type",
            type=str,
            choices=("machine_reg", "storage_reg"),
            help="Secret type to create",
        )
        parser.add_argument(
            "--name", type=str, default=None, help="Name assigned to secret"
        )
        parser.add_argument(
            "--raw", action="store_true", help="Output created secret directly"
        )

    def handle(self, *args, **options):
        if options["name"] is None:
            if options["secret_type"] == "storage_reg":
                options["name"] = "Storage Registrations"
            else:
                options["name"] = "Machine Registrations"

        secret = hashers.get_random_string(30)
        auth = Auth()
        auth.active = True
        auth.name = options["name"]
        auth.secret_hash = hashers.make_password(secret)
        auth.secret_type = options["secret_type"]
        auth.save()

        if options["raw"]:
            self.stdout.write(secret)
        else:
            self.stdout.write(
                "New registration secret created: {} ({})".format(
                    secret, options["name"]
                )
            )
