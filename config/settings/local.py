from .base import *
from decouple import config

# GENERAL
# --------------------------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = [
  'localhost',
  '0.0.0.0',
  '127.0.0.1',
]
INTERNAL_IPS = [
  '127.0.0.1',
]


# DATABASES
# --------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


# STATIC FILES (CSS, JS, IMAGES)
# --------------------------------------------------------------------
STATIC_ROOT = BASE_DIR / "hittalaget" / "staticfiles"
STATIC_URL = '/static/'
STATICFILES_DIRS = [
  BASE_DIR / "hittalaget" / "static",
]


# MEDIA FILES (UPLOADED BY USERS)
# --------------------------------------------------------------------
MEDIA_ROOT = BASE_DIR / "hittalaget" / "media"
MEDIA_URL = '/media/'


# EMAIL
# --------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"




