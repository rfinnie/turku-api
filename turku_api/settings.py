import os
from database_settings import DATABASES
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = 's+*j4$4pnqg_@(1z7%=e9a-cs$gn0np*^_)f1h$&*5xyz-hp34'
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ['turku.canonical.com']
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'turku_api',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
ROOT_URLCONF = 'turku_api.urls'
WSGI_APPLICATION = 'turku_api.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
