# SPDX-PackageSummary: Turku backups - API server
# SPDX-FileCopyrightText: Copyright (C) 2015-2020 Canonical Ltd.
# SPDX-FileCopyrightText: Copyright (C) 2015-2021 Ryan Finnie <ryan@finnie.org>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
