from .base import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": "localhost",
        "PORT": "",
        "NAME": "emma",
        "USER": "nazariyg",
        "PASSWORD": get_env_variable("DJANGO_DB_PASSWORD"),
    }
}

INSTALLED_APPS += ("debug_toolbar", )
MIDDLEWARE_CLASSES += ("debug_toolbar.middleware.DebugToolbarMiddleware", )
