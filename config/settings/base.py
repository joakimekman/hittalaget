import os
from decouple import config
from pathlib import Path


# PATHS
# --------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
APPS_DIR = BASE_DIR / 'hittalaget'


# SECRET KEY
# --------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY')


# APPS
# --------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'django_extensions',
    'debug_toolbar',
]
LOCAL_APPS = [
    'hittalaget.users.apps.UsersConfig',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# MIDDLEWARE
# --------------------------------------------------------------------
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# URLs
# --------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# TEMPLATES
# --------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR / 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# INTERNATIONALIZATION
# --------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# AUTHENTICATION
# --------------------------------------------------------------------
AUTH_USER_MODEL = 'users.User'
LOGIN_URL = 'user:login'
LOGIN_REDIRECT_URL = 'user:redirect'
LOGOUT_REDIRECT_URL = LOGIN_URL






