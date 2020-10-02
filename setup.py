#!/usr/bin/env python3

# Turku backups - API application
# Copyright 2015-2020 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup


setup(
    name="turku_api",
    description="Turku backups - API application",
    author="Ryan Finnie",
    url="https://launchpad.net/turku",
    python_requires="~=3.4",
    packages=["turku_api", "turku_api.management.commands"],
    include_package_data=True,
    install_requires=["Django"],
)
