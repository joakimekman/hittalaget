from .base import *
from decouple import config


# GENERAL
# --------------------------------------------------------------------
DEBUG = False
ALLOWED_HOSTS = [
  'localhost',
  '0.0.0.0',
  '127.0.0.1',
]


# DATABASES
# --------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


# PASSWORDS
# --------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


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








