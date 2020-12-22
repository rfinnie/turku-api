#!/usr/bin/env python3

# Turku backups - API server
# Copyright (C) 2015-2020 Canonical Ltd., Ryan Finnie and other contributors
#
# SPDX-License-Identifer: AGPL-3.0-or-later

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turku_api.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
