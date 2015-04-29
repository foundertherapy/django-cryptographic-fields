from django.test import TestCase

import models


class TestModelTestCase(TestCase):
    def test_value(self):
        inst = models.TestModel()
        inst.enc_char_field = 'This is a test string!'
        inst.save()

        inst2 = models.TestModel.objects.get()
        self.assertEqual(inst2.enc_char_field, 'This is a test string!')

    def test_unicode_value(self):
        inst = models.TestModel()
        inst.enc_char_field = u'\xa2\u221e\xa7\xb6\u2022\xaa'
        inst.save()

        inst2 = models.TestModel.objects.get()
        self.assertEqual(inst2.enc_char_field, u'\xa2\u221e\xa7\xb6\u2022\xaa')

    def test_raw_value(self):
        inst = models.TestModel()
        inst.enc_char_field = 'This is a test string!'
        inst.save()

        v = models.TestModel.objects.values_list('enc_char_field', flat=True)
        self.assertEqual(v[0][:7], u'gAAAAAB')
