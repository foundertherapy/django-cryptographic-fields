from __future__ import unicode_literals

import sys

import django.db
import django.db.models
from django.utils.six import PY2, string_types
from django.utils.functional import cached_property
from django.core import validators
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import cryptography.fernet


def get_crypter():
    configured_keys = getattr(settings, 'FIELD_ENCRYPTION_KEY')

    if configured_keys is None:
        raise ImproperlyConfigured('FIELD_ENCRYPTION_KEY must be defined in settings')

    try:
        # Allow the use of key rotation
        if isinstance(configured_keys, (tuple, list)):
            keys = [cryptography.fernet.Fernet(str(k)) for k in configured_keys]
        else:
            # else turn the single key into a list of one
            keys = [cryptography.fernet.Fernet(str(configured_keys)), ]
    except Exception as e:
        raise ImproperlyConfigured(
            'FIELD_ENCRYPTION_KEY defined incorrectly: {}'.format(str(e))), None, sys.exc_info()[2]

    if len(keys) == 0:
        raise ImproperlyConfigured('No keys defined in setting FIELD_ENCRYPTION_KEY')

    return cryptography.fernet.MultiFernet(keys)


CRYPTER = get_crypter()


def encrypt_str(s):
    # be sure to encode the string to bytes
    return CRYPTER.encrypt(s.encode('utf-8'))


def decrypt_str(t):
    # be sure to decode the bytes to a string
    return CRYPTER.decrypt(t.encode('utf-8')).decode('utf-8')


def calc_encrypted_length(n):
    # calculates the characters necessary to hold an encrypted string of
    # n bytes
    return len(encrypt_str('a' * n))


class EncryptedMixin(object):
    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, (bytes, string_types[0])):
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            try:
                value = decrypt_str(value)
            except cryptography.fernet.InvalidToken:
                pass

        return super(EncryptedMixin, self).to_python(value)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def get_db_prep_save(self, value, connection):
        value = super(EncryptedMixin, self).get_db_prep_save(
            value, connection)

        if value is None:
            return value
        if PY2:
            return encrypt_str(unicode(value))
        # decode the encrypted value to a unicode string, else this breaks in pgsql
        return (encrypt_str(str(value))).decode('utf-8')

    def get_internal_type(self):
        return "TextField"

    def deconstruct(self):
        name, path, args, kwargs = super(EncryptedMixin, self).deconstruct()

        if 'max_length' in kwargs:
            del kwargs['max_length']

        return name, path, args, kwargs


class EncryptedCharField(EncryptedMixin, django.db.models.CharField):

    pass


class EncryptedTextField(EncryptedMixin, django.db.models.TextField):
    pass


class EncryptedDateField(EncryptedMixin, django.db.models.DateField):
    pass


class EncryptedDateTimeField(EncryptedMixin, django.db.models.DateTimeField):
    pass


class EncryptedEmailField(EncryptedMixin, django.db.models.EmailField):
    pass


class EncryptedBooleanField(EncryptedMixin, django.db.models.BooleanField):

    def get_db_prep_save(self, value, connection):
        if value is None:
            return value
        if value is True:
            value = '1'
        elif value is False:
            value = '0'
        if PY2:
            return encrypt_str(unicode(value))
        # decode the encrypted value to a unicode string, else this breaks in pgsql
        return encrypt_str(str(value)).decode('utf-8')


class EncryptedNullBooleanField(EncryptedMixin, django.db.models.NullBooleanField):

    def get_db_prep_save(self, value, connection):
        if value is None:
            return value
        if value is True:
            value = '1'
        elif value is False:
            value = '0'
        if PY2:
            return encrypt_str(unicode(value))
        # decode the encrypted value to a unicode string, else this breaks in pgsql
        return encrypt_str(str(value)).decode('utf-8')


class EncryptedNumberMixin(EncryptedMixin):
    max_length = 20

    @cached_property
    def validators(self):
        # These validators can't be added at field initialization time since
        # they're based on values retrieved from `connection`.
        range_validators = []
        internal_type = self.__class__.__name__[9:]
        min_value, max_value = django.db.connection.ops.integer_field_range(
            internal_type)
        if min_value is not None:
            range_validators.append(validators.MinValueValidator(min_value))
        if max_value is not None:
            range_validators.append(validators.MaxValueValidator(max_value))
        return super(EncryptedNumberMixin, self).validators + range_validators


class EncryptedIntegerField(EncryptedNumberMixin, django.db.models.IntegerField):
    description = "An IntegerField that is encrypted before " \
                  "inserting into a database using the python cryptography " \
                  "library"
    pass


class EncryptedPositiveIntegerField(EncryptedNumberMixin, django.db.models.PositiveIntegerField):
    pass


class EncryptedSmallIntegerField(EncryptedNumberMixin, django.db.models.SmallIntegerField):
    pass


class EncryptedPositiveSmallIntegerField(EncryptedNumberMixin, django.db.models.PositiveSmallIntegerField):
    pass


class EncryptedBigIntegerField(EncryptedNumberMixin, django.db.models.BigIntegerField):
    pass
