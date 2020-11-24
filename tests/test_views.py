# Turku backups - API server
# Copyright (C) 2015-2020 Canonical Ltd., Ryan Finnie and other contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the Affero GNU General Public License for more details.
#
# You should have received a copy of the Affero GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

from django.test import TestCase

import turku_api.views


class TestHashedint(TestCase):
    def test_valid(self):
        """Test valid data"""
        self.assertEqual(turku_api.views.hashedint(1, 100, hash_id="hello"), 71)

    def test_bytes_id(self):
        """Test bytes id"""
        self.assertEqual(turku_api.views.hashedint(1, 100, hash_id=b"\x01\x02\x03"), 26)

    def test_empty_id(self):
        """Test empty ID"""
        self.assertEqual(turku_api.views.hashedint(1, 100), 1)

    def test_invalid_id_type(self):
        """Test invalid id type raises TypeError"""
        with self.assertRaises(TypeError):
            turku_api.views.hashedint(1, 100, hash_id={1: 2})
