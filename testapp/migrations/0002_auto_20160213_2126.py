# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cryptographic_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodel',
            name='enc_char_field_no_length_conversion',
            field=cryptographic_fields.fields.EncryptedCharField(null=True, max_length=396),
        ),
    ]
