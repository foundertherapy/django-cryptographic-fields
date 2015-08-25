import random
import string

import cryptography.fernet

from django.core import validators
from django.conf import settings
import django.db
import django.db.models
from django.utils.six import with_metaclass
from django.utils.functional import cached_property


FIELD_ENCRYPTION_KEY = settings.FIELD_ENCRYPTION_KEY
ALPHABET = string.ascii_letters + string.digits

# Allow the use of key rotation
if isinstance(FIELD_ENCRYPTION_KEY, (tuple, list)):
    keys = [cryptography.fernet.Fernet(k) for k in FIELD_ENCRYPTION_KEY]

elif isinstance(FIELD_ENCRYPTION_KEY, dict):
    # allow the keys to be indexed in a dictionary
    keys = [
        cryptography.fernet.Fernet(k) for k in FIELD_ENCRYPTION_KEY.values()
    ]
else:
    # else turn the single key into a list of one
    keys = [cryptography.fernet.Fernet(FIELD_ENCRYPTION_KEY), ]

crypter = cryptography.fernet.MultiFernet(keys)


def encrypt_str(s, salt_length):
    salt = ''.join(random.choice(ALPHABET) for i in range(salt_length))
    s = u'{salt}{string}'.format(salt=salt, string=s)
    # be sure to encode the string to bytes.
    return crypter.encrypt(s.encode('utf-8'))


def decrypt_str(t, salt_length):
    # be sure to decode the bytes to a string
    raw_text = crypter.decrypt(t.encode('utf-8')).decode('utf-8')
    # remove the salt
    return raw_text[salt_length:]


def calc_encrypted_length(n, salt_length):
    # calculates the characters necessary to hold an encrypted string of
    # n bytes
    return len(encrypt_str('a' * n, salt_length))


class EncryptedMixin(object):
    def __init__(self, *args, **kwargs):
        self.salt_length = kwargs.pop('salt_length', 2)

        super(EncryptedMixin, self).__init__(*args, **kwargs)
        # set the max_length to be large enough to contain the encrypted value
        if not self.max_length:
            self.max_length = 10
        self.unencrypted_max_length = self.max_length
        self.max_length = calc_encrypted_length(
            self.unencrypted_max_length, self.salt_length)

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, basestring):
            try:
                value = decrypt_str(value, self.salt_length)
            except cryptography.fernet.InvalidToken:
                pass

        return super(EncryptedMixin, self).to_python(value)

    def get_db_prep_save(self, value, connection):
        value = super(EncryptedMixin, self).get_db_prep_save(
            value, connection)

        if value is None:
            return value
        else:
            return encrypt_str(unicode(value), self.salt_length)

    def get_internal_type(self):
        return "CharField"


class EncryptedCharField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedMixin,
                       django.db.models.CharField)):
    pass


class EncryptedTextField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedMixin,
                       django.db.models.TextField)):
    pass

    def get_internal_type(self):
        return "TextField"


class EncryptedDateField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedMixin,
                       django.db.models.DateField)):
    pass


class EncryptedDateTimeField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedMixin,
                       django.db.models.DateTimeField)):
    pass


class EncryptedEmailField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedMixin,
                       django.db.models.EmailField)):
    pass


class EncryptedBooleanField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedMixin,
                       django.db.models.BooleanField)):
    unencrypted_max_length = 10

    def get_db_prep_save(self, value, connection):
        if value is None:
            return value
        if value is True:
            value = '1'
        elif value is False:
            value = '0'
        return encrypt_str(unicode(value), self.salt_length)


class EncryptedNullBooleanField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedMixin,
                       django.db.models.NullBooleanField)):
    unencrypted_max_length = 10

    def get_db_prep_save(self, value, connection):
        if value is None:
            return value
        if value is True:
            value = '1'
        elif value is False:
            value = '0'
        return encrypt_str(unicode(value), self.salt_length)


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


class EncryptedIntegerField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedNumberMixin,
                       django.db.models.IntegerField)):
    description = "An IntegerField that is encrypted before " \
                  "inserting into a database using the python cryptography " \
                  "library"
    pass


class EncryptedPositiveIntegerField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedNumberMixin,
                       django.db.models.PositiveIntegerField)):
    pass


class EncryptedSmallIntegerField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedNumberMixin,
                       django.db.models.SmallIntegerField)):
    pass


class EncryptedPositiveSmallIntegerField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedNumberMixin,
                       django.db.models.PositiveSmallIntegerField)):
    pass


class EncryptedBigIntegerField(
        with_metaclass(django.db.models.SubfieldBase, EncryptedNumberMixin,
                       django.db.models.BigIntegerField)):
    pass


