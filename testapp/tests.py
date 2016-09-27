from __future__ import unicode_literals

import datetime
import mock

from django.forms import ModelForm
from django.test import TestCase
from django.utils import timezone

import cryptography.fernet
import cryptographic_fields.fields

from . import models


class TestModelTestCase(TestCase):
    def test_value(self):
        test_date_today = datetime.date.today()
        test_date = datetime.date(2011, 1, 1)
        test_datetime = datetime.datetime(2011, 1, 1, 1, tzinfo=timezone.utc)
        inst = models.TestModel()
        inst.enc_char_field = 'This is a test string!'
        inst.enc_text_field = 'This is a test string2!'
        inst.enc_date_field = test_date
        inst.enc_datetime_field = test_datetime
        inst.enc_boolean_field = True
        inst.enc_null_boolean_field = True
        inst.enc_integer_field = 123456789
        inst.enc_positive_integer_field = 123456789
        inst.enc_small_integer_field = 123456789
        inst.enc_positive_small_integer_field = 123456789
        inst.enc_big_integer_field = 9223372036854775807
        inst.save()

        inst = models.TestModel.objects.get()
        self.assertEqual(inst.enc_char_field, 'This is a test string!')
        self.assertEqual(inst.enc_text_field, 'This is a test string2!')
        self.assertEqual(inst.enc_date_field, test_date)
        self.assertEqual(inst.enc_date_now_field, test_date_today)
        self.assertEqual(inst.enc_date_now_add_field, test_date_today)
        # be careful about sqlite testing, which doesn't support native dates
        if timezone.is_naive(inst.enc_datetime_field):
            inst.enc_datetime_field = timezone.make_aware(inst.enc_datetime_field, timezone.utc)
        self.assertEqual(inst.enc_datetime_field, test_datetime)
        self.assertEqual(inst.enc_boolean_field, True)
        self.assertEqual(inst.enc_null_boolean_field, True)
        self.assertEqual(inst.enc_integer_field, 123456789)
        self.assertEqual(inst.enc_positive_integer_field, 123456789)
        self.assertEqual(inst.enc_small_integer_field, 123456789)
        self.assertEqual(inst.enc_positive_small_integer_field, 123456789)
        self.assertEqual(inst.enc_big_integer_field, 9223372036854775807)

        test_date = datetime.date(2012, 2, 1)
        test_datetime = datetime.datetime(2012, 1, 1, 2, tzinfo=timezone.utc)
        inst.enc_char_field = 'This is another test string!'
        inst.enc_text_field = 'This is another test string2!'
        inst.enc_date_field = test_date
        inst.enc_datetime_field = test_datetime
        inst.enc_boolean_field = False
        inst.enc_null_boolean_field = False
        inst.enc_integer_field = -123456789
        inst.enc_positive_integer_field = 0
        inst.enc_small_integer_field = -123456789
        inst.enc_positive_small_integer_field = 0
        inst.enc_big_integer_field = -9223372036854775806
        inst.save()

        inst = models.TestModel.objects.get()
        self.assertEqual(inst.enc_char_field, 'This is another test string!')
        self.assertEqual(inst.enc_text_field, 'This is another test string2!')
        self.assertEqual(inst.enc_date_field, test_date)
        self.assertEqual(inst.enc_date_now_field, datetime.date.today())
        self.assertEqual(inst.enc_date_now_add_field, datetime.date.today())
        # be careful about sqlite testing, which doesn't support native dates
        if timezone.is_naive(inst.enc_datetime_field):
            inst.enc_datetime_field = timezone.make_aware(inst.enc_datetime_field, timezone.utc)
        self.assertEqual(inst.enc_datetime_field, test_datetime)
        self.assertEqual(inst.enc_boolean_field, False)
        self.assertEqual(inst.enc_null_boolean_field, False)
        self.assertEqual(inst.enc_integer_field, -123456789)
        self.assertEqual(inst.enc_positive_integer_field, 0)
        self.assertEqual(inst.enc_small_integer_field, -123456789)
        self.assertEqual(inst.enc_positive_small_integer_field, 0)
        self.assertEqual(inst.enc_big_integer_field, -9223372036854775806)

        inst.enc_null_boolean_field = None
        inst.save()
        inst = models.TestModel.objects.get()
        self.assertEqual(inst.enc_null_boolean_field, None)

    def test_unicode_value(self):
        inst = models.TestModel()
        inst.enc_char_field = u'\xa2\u221e\xa7\xb6\u2022\xaa'
        inst.enc_text_field = u'\xa2\u221e\xa7\xb6\u2022\xa2'
        inst.save()

        inst2 = models.TestModel.objects.get()
        self.assertEqual(inst2.enc_char_field, u'\xa2\u221e\xa7\xb6\u2022\xaa')
        self.assertEqual(inst2.enc_text_field, u'\xa2\u221e\xa7\xb6\u2022\xa2')

    @mock.patch('django.db.models.sql.compiler.SQLCompiler.get_converters')
    def test_raw_value(self, get_converters_method):
        get_converters_method.return_value = []

        inst = models.TestModel()
        inst.enc_char_field = 'This is a test string!'
        inst.enc_text_field = 'This is a test string2!'
        inst.enc_date_field = datetime.date(2011, 1, 1)
        inst.enc_datetime_field = datetime.datetime(2012, 2, 1, 1, tzinfo=timezone.UTC())
        inst.enc_boolean_field = True
        inst.enc_null_boolean_field = True
        inst.enc_integer_field = 123456789
        inst.enc_positive_integer_field = 123456789
        inst.enc_small_integer_field = 123456789
        inst.enc_positive_small_integer_field = 123456789
        inst.enc_big_integer_field = 9223372036854775807
        inst.save()

        d = models.TestModel.objects.values()[0]
        for key, value in d.items():
            if key == 'id':
                continue
            self.assertEqual(value[:7], 'gAAAAAB', '{} failed: {}'.format(key, value))

        inst.enc_null_boolean_field = None
        inst.save()

        d = models.TestModel.objects.values()[0]
        self.assertEqual(d['enc_null_boolean_field'], None)

    def test_get_internal_type(self):
        enc_char_field = models.TestModel._meta.fields[1]
        enc_text_field = models.TestModel._meta.fields[2]
        enc_date_field = models.TestModel._meta.fields[3]
        enc_date_now_field = models.TestModel._meta.fields[4]
        enc_boolean_field = models.TestModel._meta.fields[7]
        enc_null_boolean_field = models.TestModel._meta.fields[8]
        enc_integer_field = models.TestModel._meta.fields[9]
        enc_positive_integer_field = models.TestModel._meta.fields[10]
        enc_small_integer_field = models.TestModel._meta.fields[11]
        enc_positive_small_integer_field = models.TestModel._meta.fields[12]
        enc_big_integer_field = models.TestModel._meta.fields[13]

        self.assertEqual(enc_char_field.get_internal_type(), 'TextField')
        self.assertEqual(enc_text_field.get_internal_type(), 'TextField')
        self.assertEqual(enc_date_field.get_internal_type(), 'TextField')
        self.assertEqual(enc_date_now_field.get_internal_type(), 'TextField')
        self.assertEqual(enc_boolean_field.get_internal_type(), 'TextField')
        self.assertEqual(enc_null_boolean_field.get_internal_type(), 'TextField')

        self.assertEqual(enc_integer_field.get_internal_type(), 'TextField')
        self.assertEqual(enc_positive_integer_field.get_internal_type(), 'TextField')
        self.assertEqual(enc_small_integer_field.get_internal_type(), 'TextField')
        self.assertEqual(enc_positive_small_integer_field.get_internal_type(), 'TextField')
        self.assertEqual(enc_big_integer_field.get_internal_type(), 'TextField')

    def test_auto_date(self):
        enc_date_now_field = models.TestModel._meta.fields[4]
        self.assertEqual(enc_date_now_field.name, 'enc_date_now_field')
        self.assertTrue(enc_date_now_field.auto_now)

        enc_date_now_add_field = models.TestModel._meta.fields[5]
        self.assertEqual(enc_date_now_add_field.name, 'enc_date_now_add_field')
        self.assertFalse(enc_date_now_add_field.auto_now)

        self.assertFalse(enc_date_now_field.auto_now_add)
        self.assertTrue(enc_date_now_add_field.auto_now_add)

    def test_max_length_validation(self):
        class TestModelForm(ModelForm):
            class Meta:
                model = models.TestModel
                fields = ('enc_char_field', )

        f = TestModelForm(data={'enc_char_field': 'a' * 200})
        self.assertFalse(f.is_valid())

        f = TestModelForm(data={'enc_char_field': 'a' * 99})
        self.assertTrue(f.is_valid())

    def test_rotating_keys(self):
        key1 = cryptography.fernet.Fernet.generate_key()
        key2 = cryptography.fernet.Fernet.generate_key()

        with self.settings(FIELD_ENCRYPTION_KEY=key1):
            # make sure we update the crypter with the new key
            cryptographic_fields.fields.CRYPTER = cryptographic_fields.fields.get_crypter()

            test_date_today = datetime.date.today()
            test_date = datetime.date(2011, 1, 1)
            test_datetime = datetime.datetime(2011, 1, 1, 1, tzinfo=timezone.utc)
            inst = models.TestModel()
            inst.enc_char_field = 'This is a test string!'
            inst.enc_text_field = 'This is a test string2!'
            inst.enc_date_field = test_date
            inst.enc_datetime_field = test_datetime
            inst.enc_boolean_field = True
            inst.enc_null_boolean_field = True
            inst.enc_integer_field = 123456789
            inst.enc_positive_integer_field = 123456789
            inst.enc_small_integer_field = 123456789
            inst.enc_positive_small_integer_field = 123456789
            inst.enc_big_integer_field = 9223372036854775807
            inst.save()

        # test that loading the instance from the database results in usable data
        # (since it uses the older key that's still configured)
        with self.settings(FIELD_ENCRYPTION_KEY=[key2, key1]):
            # make sure we update the crypter with the new key
            cryptographic_fields.fields.CRYPTER = cryptographic_fields.fields.get_crypter()

            inst = models.TestModel.objects.get()
            self.assertEqual(inst.enc_char_field, 'This is a test string!')
            self.assertEqual(inst.enc_text_field, 'This is a test string2!')
            self.assertEqual(inst.enc_date_field, test_date)
            self.assertEqual(inst.enc_date_now_field, test_date_today)
            self.assertEqual(inst.enc_date_now_add_field, test_date_today)
            # be careful about sqlite testing, which doesn't support native dates
            if timezone.is_naive(inst.enc_datetime_field):
                inst.enc_datetime_field = timezone.make_aware(inst.enc_datetime_field, timezone.utc)
            self.assertEqual(inst.enc_datetime_field, test_datetime)
            self.assertEqual(inst.enc_boolean_field, True)
            self.assertEqual(inst.enc_null_boolean_field, True)
            self.assertEqual(inst.enc_integer_field, 123456789)
            self.assertEqual(inst.enc_positive_integer_field, 123456789)
            self.assertEqual(inst.enc_small_integer_field, 123456789)
            self.assertEqual(inst.enc_positive_small_integer_field, 123456789)
            self.assertEqual(inst.enc_big_integer_field, 9223372036854775807)

            # save the instance to rotate the key
            inst.save()

        # test that saving the instance results in key rotation to the correct key
        with self.settings(FIELD_ENCRYPTION_KEY=[key2, ]):
            # make sure we update the crypter with the new key
            cryptographic_fields.fields.CRYPTER = cryptographic_fields.fields.get_crypter()

            # test that loading the instance from the database results in usable data
            # (since it uses the older key that's still configured)
            inst = models.TestModel.objects.get()
            self.assertEqual(inst.enc_char_field, 'This is a test string!')
            self.assertEqual(inst.enc_text_field, 'This is a test string2!')
            self.assertEqual(inst.enc_date_field, test_date)
            self.assertEqual(inst.enc_date_now_field, test_date_today)
            self.assertEqual(inst.enc_date_now_add_field, test_date_today)
            # be careful about sqlite testing, which doesn't support native dates
            if timezone.is_naive(inst.enc_datetime_field):
                inst.enc_datetime_field = timezone.make_aware(inst.enc_datetime_field, timezone.utc)
            self.assertEqual(inst.enc_datetime_field, test_datetime)
            self.assertEqual(inst.enc_boolean_field, True)
            self.assertEqual(inst.enc_null_boolean_field, True)
            self.assertEqual(inst.enc_integer_field, 123456789)
            self.assertEqual(inst.enc_positive_integer_field, 123456789)
            self.assertEqual(inst.enc_small_integer_field, 123456789)
            self.assertEqual(inst.enc_positive_small_integer_field, 123456789)
            self.assertEqual(inst.enc_big_integer_field, 9223372036854775807)

        # test that the instance with rotated key is no longer readable using the old key
        with self.settings(FIELD_ENCRYPTION_KEY=[key1, ]):
            # make sure we update the crypter with the new key
            cryptographic_fields.fields.CRYPTER = cryptographic_fields.fields.get_crypter()

            # test that loading the instance from the database results in usable data
            # (since it uses the older key that's still configured)
            # Note we need to only load the enc_char_field because loading date field types results in conversion to python dates,
            # which will be raise a ValidationError when the field can't be properly decoded
            inst = models.TestModel.objects.only('enc_char_field').get()
            self.assertNotEqual(inst.enc_char_field, 'This is a test string!')
            self.assertEqual(inst.enc_char_field[:5], 'gAAAA')

        # reset the CRYPTER since we screwed with the default configuration with this test
        cryptographic_fields.fields.CRYPTER = cryptographic_fields.fields.get_crypter()

