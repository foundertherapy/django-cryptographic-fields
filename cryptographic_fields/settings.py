from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


FIELD_ENCRYPTION_KEY = getattr(settings, 'FIELD_ENCRYPTION_KEY')

if not FIELD_ENCRYPTION_KEY:
    raise ImproperlyConfigured(
        'FIELD_ENCRYPTION_KEY must be defined in settings')
