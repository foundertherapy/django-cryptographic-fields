# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cryptographic_fields.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enc_char_field', cryptographic_fields.fields.EncryptedCharField(max_length=396)),
                ('enc_text_field', cryptographic_fields.fields.EncryptedTextField()),
                ('enc_date_field', cryptographic_fields.fields.EncryptedDateField(max_length=100)),
                ('enc_date_now_field', cryptographic_fields.fields.EncryptedDateField(max_length=100, editable=False, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
