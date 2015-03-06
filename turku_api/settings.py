import os
import random
import string

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
SECRET_KEY = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(30))

try:
    from local_settings import *
except ImportError:
    pass
try:
    from database_settings import *
except ImportError:
    pass
try:
    from secret_settings import *
except ImportError:
    pass
