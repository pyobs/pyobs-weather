"""
Django settings for pyobs_weather project.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SECRET_KEY", "changeme")

DEBUG = os.environ.get("DEBUG", "1") == "1"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "http://localhost").split(",")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "pyobs_weather.weather",
    "pyobs_weather.frontend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pyobs_weather.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pyobs_weather.wsgi.application"


# Database

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("SQL_DATABASE", "postgres"),
        "USER": os.environ.get("SQL_USER", "postgres"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "postgres"),
        "HOST": os.environ.get("SQL_HOST", "db"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Static files

ROOT_URL = os.environ.get("ROOT_URL", "/")
STATIC_URL = ROOT_URL + "static/"
STATIC_ROOT = os.environ.get("STATIC_ROOT", "/static/")


# Celery / RabbitMQ

BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")


# Weather sensors

WEATHER_SENSORS = os.environ.get(
    "WEATHER_SENSORS", "temp,humid,press,windspeed,winddir,rain,skytemp,sunalt"
).split(",")
WEATHER_PLOTS = os.environ.get(
    "WEATHER_PLOTS", "temp,humid,press,windspeed,winddir,rain,skytemp"
).split(",")


# Observer

OBSERVER_NAME = os.environ.get("OBSERVER_NAME", "MONET/N @ McDonald Observatory")
OBSERVER_LOCATION = {
    "longitude": float(os.environ.get("OBSERVER_LONGITUDE", "-104.0217")),
    "latitude": float(os.environ.get("OBSERVER_LATITUDE", "30.6717")),
    "elevation": float(os.environ.get("OBSERVER_ELEVATION", "2075.0")),
}

WINDOW_TITLE = os.environ.get("WINDOW_TITLE", "Weather at " + OBSERVER_NAME)


# InfluxDB

USE_INFLUX = os.environ.get("USE_INFLUX", "1") == "1"
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN", "")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "weather")
INFLUXDB_BUCKET_5MIN = os.environ.get("INFLUXDB_BUCKET_5MIN", "weather_average")
INFLUXDB_MEASUREMENT_AVERAGE = os.environ.get("INFLUXDB_MEASUREMENT_AVERAGE", "average")


# try to import a local_settings.py
try:
    from .local_settings import *
except ImportError:
    pass
