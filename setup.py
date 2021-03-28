#!/usr/bin/env python3

# SPDX-PackageSummary: Turku backups - API server
# SPDX-FileCopyrightText: Copyright (C) 2015-2020 Canonical Ltd.
# SPDX-FileCopyrightText: Copyright (C) 2015-2021 Ryan Finnie <ryan@finnie.org>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from setuptools import setup


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding="utf-8") as f:
        return f.read()


setup(
    name="turku_api",
    description="Turku backups - API application",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Ryan Finnie",
    url="https://github.com/rfinnie/turku-api",
    python_requires="~=3.4",
    packages=["turku_api", "turku_api.management.commands"],
    include_package_data=True,
    install_requires=["Django"],
)
