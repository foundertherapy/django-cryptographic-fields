Django Cryptographic Fields
===========================

.. image:: https://circleci.com/gh/foundertherapy/django-cryptographic-fields.png
   :target: https://circleci.com/gh/foundertherapy/django-cryptographic-fields

About
-----

``django-cryptographic-fields`` is set of fields that wrap standard Django
fields with encryption provided by the python cryptography library. These
fields are much more compatible with a 12-factor design since they take their
encryption key from the settings file instead of a file on disk used by
``keyczar``.

While keyczar is an excellent tool to use for encryption, it's not compatible
with Python 3, and it requires, for hosts like Heroku, that you either check
your key file into your git repository for deployment, or implement manual
post-deployment processing to write the key stored in an environment variable
into a file that keyczar can read.

Getting Started
---------------

    $ pip install django-cryptographic-fields

Add "cryptographic_fields" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = (
        ...
        'cryptographic_fields',
    )

``django-cryptographic-fields`` expects the encryption key to be specified
using ``FIELD_ENCRYPTION_KEY`` in your project's ``settings.py`` file. For
example, to load it from the local environment:

    import os

    FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY', '')

To use an encrypted field in a Django model, use one of the fields from the
``cryptographic_fields`` module:

    from cryptographic_fields.fields import EncryptedCharField

    class EncryptedFieldModel(models.Model):
        encrypted_char_field = EncryptedCharField(encrypted_max_length=100)

Determining Encrypted Field Length
----------------------------------

For fields that require ``max_length`` to be specified, you will want to specify
``encrypted_max_length`` instead of ``max_length``. There is a management
command to calculate the correct size of ``encrypted_max_length``. So, for a
field that would normally have a ``max_length`` of 50, you would run the
following command to get the correct value for ``encrypted_max_length``.

    ./manage.py calculate_max_length 50

You would then use the resulting value to specify ``encrypted_max_length`` in
your models, instead of passing the traditional ``max_length`` argument.

**Note** that if you decide to skip this step and simply specify ``max_length``,
the ``Encrypted`` variants of those fields will automatically increase the
size of the database field to hold the encrypted form of the content. For
example, a 3 character CharField will automatically specify a database
field size of 100 characters when ``EncryptedCharField(max_length=3)``
is specified. The problem with this is that ``django-admin makemigrations`` will
always create a migration, because it will see that the ``max_length`` of the
actual model object is different than what you have specified.

Generating an Encryption Key
----------------------------

There is a Django management command ``generate_encryption_key`` provided
with the ``cryptographic_fields`` library. Use this command to generate a new
encryption key to set as ``settings.FIELD_ENCRYPTION_KEY``.

    ./manage.py generate_encryption_key

Running this command will print an encryption key to the terminal, which can
be configured in your environment or settings file.

Limitations
-----------

Due to the nature of the encrypted data, filtering by values contained in
encrypted fields won't work properly. Sorting is also not supported.
