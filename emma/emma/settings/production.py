from .base import *


DEBUG = False
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
