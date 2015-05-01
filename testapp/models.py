import django.db.models

from cryptographic_fields import fields


class TestModel(django.db.models.Model):
    enc_char_field = fields.EncryptedCharField(max_length=100)
    enc_text_field = fields.EncryptedTextField()
    enc_date_field = fields.EncryptedDateField(null=True)
    enc_date_now_field = fields.EncryptedDateField(auto_now=True, null=True)
    enc_date_now_add_field = fields.EncryptedDateField(
        auto_now_add=True, null=True)
    enc_datetime_field = fields.EncryptedDateTimeField(null=True)
    enc_boolean_field = fields.EncryptedBooleanField(default=True)
    enc_null_boolean_field = fields.EncryptedNullBooleanField()
    enc_integer_field = fields.EncryptedIntegerField(null=True)
    enc_positive_integer_field = fields.EncryptedPositiveIntegerField(null=True)
    enc_small_integer_field = fields.EncryptedSmallIntegerField(null=True)
    enc_positive_small_integer_field = \
        fields.EncryptedPositiveSmallIntegerField(null=True)
    enc_big_integer_field = fields.EncryptedBigIntegerField(null=True)
