from .base import *

DEBUG = True

# En dev, les emails s'affichent dans le terminal au lieu d'être envoyés
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SQLite optionnel en dev si tu ne veux pas PostgreSQL localement
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# Django Debug Toolbar (optionnel)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']
