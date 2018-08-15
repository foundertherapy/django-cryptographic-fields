INTERNAL_IPS = ('127.0.0.1', )
ALLOWED_HOSTS = ['localhost', '127.0.0.1', ]
APPEND_SLASH = True
TIME_ZONE = 'UTC'
USE_TZ = True
ROOT_URLCONF = 'testapp.urls'
SECRET_KEY = 'abc'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django_coverage',
    'cryptographic_fields',
    'testapp',
)

FIELD_ENCRYPTION_KEY = '6-QgONW6TUl5rt4Xq8u-wBwPcb15sIYS2CN6d69zueM='

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USERNAME': 'ubuntu',
        'HOST': '127.0.0.1',
        'PORT': 5432,
        'NAME': 'circle_test',
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)
