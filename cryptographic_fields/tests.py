from __future__ import unicode_literals

from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

import cryptography.fernet

import fields


class TestSettings(TestCase):
    def setUp(self):
        self.key1 = cryptography.fernet.Fernet.generate_key()
        self.key2 = cryptography.fernet.Fernet.generate_key()

    def test_settings(self):
        with self.settings(FIELD_ENCRYPTION_KEY=self.key1):
            fields.get_crypter()

        with self.settings(FIELD_ENCRYPTION_KEY=(self.key1, self.key2,)):
            fields.get_crypter()

        with self.settings(FIELD_ENCRYPTION_KEY=[self.key1, self.key2, ]):
            fields.get_crypter()

    def test_settings_empty(self):
        with self.settings(FIELD_ENCRYPTION_KEY=None):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(FIELD_ENCRYPTION_KEY=''):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(FIELD_ENCRYPTION_KEY=[]):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(FIELD_ENCRYPTION_KEY=tuple()):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

    def test_settings_bad(self):
        with self.settings(FIELD_ENCRYPTION_KEY=self.key1[:5]):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(FIELD_ENCRYPTION_KEY=(self.key1[:5], self.key2,)):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(FIELD_ENCRYPTION_KEY=[self.key1[:5], self.key2[:5], ]):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)
