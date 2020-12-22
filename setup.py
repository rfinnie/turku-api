#!/usr/bin/env python3

# Turku backups - API application
# Copyright 2015-2020 Canonical Ltd., Ryan Finnie and other contributors
#
# SPDX-License-Identifer: AGPL-3.0-or-later

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
