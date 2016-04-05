from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


FIELD_ENCRYPTION_KEY = str(getattr(settings, 'FIELD_ENCRYPTION_KEY'))

if FIELD_ENCRYPTION_KEY is None:
    raise ImproperlyConfigured(
            'FIELD_ENCRYPTION_KEY must be defined in settings')
