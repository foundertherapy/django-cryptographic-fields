import datetime

import django.db.models
import django.core.exceptions
from django.utils.six import with_metaclass

from settings import FIELD_ENCRYPTION_KEY

import cryptography.fernet


crypter = cryptography.fernet.Fernet(FIELD_ENCRYPTION_KEY)


def encrypt_str(s):
    # be sure to encode the string to bytes
    return crypter.encrypt(s.encode('utf-8'))


def decrypt_str(t):
    # be sure to decode the bytes to a string
    return crypter.decrypt(t.encode('utf-8')).decode('utf-8')


def calc_encrypted_length(n):
    # calculates the characters necessary to hold an encrypted string of n bytes
    return len(encrypt_str('a' * n))


class EncryptedCharField(
        with_metaclass(django.db.models.SubfieldBase,
                       django.db.models.CharField)):
    description = "A CharField that is encrypted before inserting into a " \
                  "database using the python cryptography library"

    def __init__(self, *args, **kwargs):
        super(EncryptedCharField, self).__init__(*args, **kwargs)
        # set the max_length to be large enough to contain the encrypted value
        self.unencrypted_max_length = self.max_length
        self.max_length = calc_encrypted_length(self.unencrypted_max_length)

    def to_python(self, value):
        if value:
            try:
                return decrypt_str(value)
            except cryptography.fernet.InvalidToken:
                return value

    def get_db_prep_save(self, value, connection):
        value = super(EncryptedCharField, self).get_db_prep_save(
            value, connection)
        if value:
            return encrypt_str(value)
        else:
            return ''


class EncryptedTextField(
        with_metaclass(django.db.models.SubfieldBase,
                       django.db.models.TextField)):
    description = "A TextField that is encrypted before inserting into a " \
                  "database using the python cryptography library"

    def to_python(self, value):
        if value:
            try:
                return decrypt_str(value)
            except cryptography.fernet.InvalidToken:
                return value

    def get_db_prep_save(self, value, connection):
        value = super(EncryptedTextField, self).get_db_prep_save(
            value, connection)
        if value:
            return encrypt_str(value)
        else:
            return ''


class EncryptedDateField(
        with_metaclass(django.db.models.SubfieldBase,
                       django.db.models.DateField)):
    description = "A DateField that is encrypted before inserting into a " \
                  "database using the python cryptography library"

    def __init__(self, verbose_name=None, name=None, auto_now=False,
                 auto_now_add=False, **kwargs):
        self.auto_now, self.auto_now_add = auto_now, auto_now_add
        if auto_now or auto_now_add:
            kwargs['editable'] = False
            kwargs['blank'] = True
        super(EncryptedDateField, self).__init__(verbose_name, name, **kwargs)
        # set the max_length to be large enough to contain the encrypted value
        self.unencrypted_max_length = 10
        self.max_length = calc_encrypted_length(self.unencrypted_max_length)

    def to_python(self, value):
        if not value:
            return value

        if isinstance(value, basestring):
            try:
                value = decrypt_str(value)
            except cryptography.fernet.InvalidToken:
                pass

        return super(EncryptedDateField, self).to_python(value)

    def get_db_prep_save(self, value, connection):
        value = super(EncryptedDateField, self).get_db_prep_save(
            value, connection)

        if value:
            return encrypt_str(value)
        else:
            return ''

    def get_internal_type(self):
        return 'CharField'
