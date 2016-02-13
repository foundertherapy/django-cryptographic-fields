from __future__ import unicode_literals

import datetime

from cryptographic_fields.fields import calc_encrypted_length
from django.test import TestCase
from django.utils import timezone

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
            inst.enc_datetime_field = timezone.make_aware(
                inst.enc_datetime_field, timezone.utc)
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
        self.assertEqual(
            inst.enc_char_field, 'This is another test string!')
        self.assertEqual(
            inst.enc_text_field, 'This is another test string2!')
        self.assertEqual(inst.enc_date_field, test_date)
        self.assertEqual(inst.enc_date_now_field, datetime.date.today())
        self.assertEqual(inst.enc_date_now_add_field, datetime.date.today())
        # be careful about sqlite testing, which doesn't support native dates
        if timezone.is_naive(inst.enc_datetime_field):
            inst.enc_datetime_field = timezone.make_aware(
                inst.enc_datetime_field, timezone.utc)
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

    def test_raw_value(self):
        inst = models.TestModel()
        inst.enc_char_field_no_length_conversion = 'This is a test string!'
        inst.enc_char_field = 'This is a test string!'
        inst.enc_text_field = 'This is a test string2!'
        inst.enc_date_field = datetime.date(2011, 1, 1)
        inst.enc_datetime_field = datetime.datetime(
            2012, 2, 1, 1, tzinfo=timezone.UTC())
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
            self.assertEqual(
                value[:7], 'gAAAAAB', '{} failed: {}'.format(key, value))

        inst.enc_null_boolean_field = None
        inst.save()

        d = models.TestModel.objects.values()[0]
        self.assertEqual(d['enc_null_boolean_field'], None)

    def test_get_internal_type(self):
        self.assertEqual(
            models.TestModel.enc_char_field.field.get_internal_type(),
            'CharField')
        self.assertEqual(
            models.TestModel.enc_text_field.field.get_internal_type(),
            'TextField')
        self.assertEqual(
            models.TestModel.enc_date_field.field.get_internal_type(),
            'CharField')
        self.assertEqual(
            models.TestModel.enc_date_now_field.field.get_internal_type(),
            'CharField')
        self.assertEqual(
            models.TestModel.enc_boolean_field.field.get_internal_type(),
            'CharField')
        self.assertEqual(
            models.TestModel.enc_null_boolean_field.field.get_internal_type(),
            'CharField')

        self.assertEqual(
            models.TestModel.enc_integer_field.field.get_internal_type(),
            'CharField')
        self.assertEqual(
            models.TestModel.enc_positive_integer_field.field.
                get_internal_type(),
            'CharField')
        self.assertEqual(
            models.TestModel.enc_small_integer_field.field.get_internal_type(),
            'CharField')
        self.assertEqual(
            models.TestModel.enc_positive_small_integer_field.field.
                get_internal_type(),
            'CharField')
        self.assertEqual(
            models.TestModel.enc_big_integer_field.field.get_internal_type(),
            'CharField')

    def test_auto_date(self):
        self.assertTrue(models.TestModel.enc_date_now_field.field.auto_now)
        self.assertFalse(models.TestModel.enc_date_now_add_field.field.auto_now)
        self.assertFalse(models.TestModel.enc_date_now_field.field.auto_now_add)
        self.assertTrue(
            models.TestModel.enc_date_now_add_field.field.auto_now_add)

    def test_field_length_conversion(self):
        """
        Ensure that length is not converted if encrypted_max_length is provided
        """
        BASE_CHAR_LENGTH = 100
        inst = models.TestModel()
        converted_char_field = inst._meta.get_field('enc_char_field')
        non_converted_char_field = inst._meta.get_field(
            'enc_char_field_no_length_conversion')
        converted_length = calc_encrypted_length(BASE_CHAR_LENGTH)
        self.assertEqual(non_converted_char_field.max_length, 100)
        self.assertEqual(converted_char_field.max_length, converted_length)
