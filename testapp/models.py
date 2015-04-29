import django.db.models

import cryptographic_fields.fields


class TestModel(django.db.models.Model):
    enc_char_field = cryptographic_fields.fields.EncryptedCharField(
        max_length=100)
    enc_text_field = cryptographic_fields.fields.EncryptedTextField()
    enc_date_field = cryptographic_fields.fields.EncryptedDateField()
    enc_date_now_field = cryptographic_fields.fields.EncryptedDateField(
        auto_now=True)
