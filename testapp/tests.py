from __future__ import unicode_literals

import datetime

from django.db import connection
from django.forms import ModelForm
from django.test import TestCase
from django.utils import timezone

from testapp.models import TestModel


class TestModelTestCase(TestCase):
    def test_value(self):
        test_date_today = datetime.date.today()
        test_date = datetime.date(2011, 1, 1)
        test_datetime = datetime.datetime(2011, 1, 1, 1, tzinfo=timezone.utc)
        inst = TestModel()
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

        inst = TestModel.objects.get()
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

        inst = TestModel.objects.get()
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
        inst = TestModel.objects.get()
        self.assertEqual(inst.enc_null_boolean_field, None)

    def test_unicode_value(self):
        inst = TestModel()
        inst.enc_char_field = u'\xa2\u221e\xa7\xb6\u2022\xaa'
        inst.enc_text_field = u'\xa2\u221e\xa7\xb6\u2022\xa2'
        inst.save()

        inst2 = TestModel.objects.get()
        self.assertEqual(inst2.enc_char_field, u'\xa2\u221e\xa7\xb6\u2022\xaa')
        self.assertEqual(inst2.enc_text_field, u'\xa2\u221e\xa7\xb6\u2022\xa2')

    def test_raw_value(self):
        inst = TestModel()
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

        # get the raw values
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM testapp_testmodel LIMIT 1')
        result = cursor.fetchone()
        # iterate through the fields
        for idx, field in enumerate(TestModel._meta.get_fields()):
            if idx == 0:
                continue
            value = result[idx]
            self.assertEqual(
                'gAAAAAB', value[:7], '{} failed: {}'.format(field.name, value))

        inst.enc_null_boolean_field = None
        inst.save()

        d = TestModel.objects.values()[0]
        self.assertEqual(d['enc_null_boolean_field'], None)

    def test_get_internal_type(self):
        self.assertEqual(
            TestModel._meta.get_field('enc_char_field').get_internal_type(),
            'TextField')
        self.assertEqual(
            TestModel._meta.get_field('enc_text_field').get_internal_type(),
            'TextField')
        self.assertEqual(
            TestModel._meta.get_field('enc_date_field').get_internal_type(),
            'TextField')
        self.assertEqual(
            TestModel._meta.get_field('enc_date_now_field').get_internal_type(),
            'TextField')
        self.assertEqual(
            TestModel._meta.get_field('enc_boolean_field').get_internal_type(),
            'TextField')
        self.assertEqual(
            TestModel._meta.get_field('enc_null_boolean_field').get_internal_type(),
            'TextField')

        self.assertEqual(
            TestModel._meta.get_field('enc_integer_field').get_internal_type(),
            'TextField')
        self.assertEqual(
            TestModel._meta.get_field('enc_positive_integer_field').get_internal_type(),
            'TextField')
        self.assertEqual(
            TestModel._meta.get_field('enc_small_integer_field').get_internal_type(),
            'TextField')
        self.assertEqual(
            TestModel._meta.get_field('enc_positive_small_integer_field').get_internal_type(),
            'TextField')
        self.assertEqual(
            TestModel._meta.get_field('enc_big_integer_field').get_internal_type(),
            'TextField')

    def test_auto_date(self):
        self.assertTrue(TestModel._meta.get_field('enc_date_now_field').auto_now)
        self.assertFalse(TestModel._meta.get_field('enc_date_now_add_field').auto_now)
        self.assertFalse(TestModel._meta.get_field('enc_date_now_field').auto_now_add)
        self.assertTrue(
            TestModel._meta.get_field('enc_date_now_add_field').auto_now_add)

    def test_max_length_validation(self):
        class TestModelForm(ModelForm):
            class Meta:
                model = TestModel
                fields = ('enc_char_field', )

        f = TestModelForm(data={'enc_char_field': 'a' * 200})
        self.assertFalse(f.is_valid())

        f = TestModelForm(data={'enc_char_field': 'a' * 99})
        self.assertTrue(f.is_valid())
