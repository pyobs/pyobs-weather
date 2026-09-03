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
    "pyobs_auth",
    "pyobs_weather.weather",
    "pyobs_weather.frontend",
    "pyobs_weather.authentication",
]

# The redirect-based OIDC flow doesn't fit AUTHENTICATION_BACKENDS' synchronous
# credential-check shape - it's handled by pyobs_auth.views instead. ModelBackend (local Django
# username/password, e.g. createsuperuser) stays the sole entry.
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # After AuthenticationMiddleware (needs request.user) - re-checks a Keycloak-backed
    # session's authorization once its access token expires, instead of only at next login.
    "pyobs_auth.middleware.KeycloakSessionRefreshMiddleware",
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

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


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


# Keycloak login (pyobs-auth)

PYOBS_AUTH = {
    "SERVER_URL": os.environ.get("KEYCLOAK_SERVER_URL", ""),
    "REALM": os.environ.get("KEYCLOAK_REALM", "pyobs"),
    "CLIENT_ID": os.environ.get("KEYCLOAK_CLIENT_ID", "weather"),
    "CLIENT_SECRET": os.environ.get("KEYCLOAK_CLIENT_SECRET", ""),
    "REDIRECT_URI": os.environ.get("KEYCLOAK_REDIRECT_URI", ""),
    "POST_LOGOUT_REDIRECT_URI": os.environ.get("KEYCLOAK_POST_LOGOUT_REDIRECT_URI", ""),
    # Optional one-click IdP login: IDP_HINT is passed to Keycloak as kc_idp_hint (skips its
    # login/IdP-selection page, going straight to that identity provider); IDP_LABEL is the
    # button label on the login page. Both are deployment-specific.
    "IDP_HINT": os.environ.get("KEYCLOAK_IDP_HINT", ""),
    "IDP_LABEL": os.environ.get("KEYCLOAK_IDP_LABEL", ""),
    "USER_RESOLVER": "pyobs_weather.authentication.keycloak.resolve_user",
    # Claims-based authorization gate: membership in this Keycloak group is what authorizes a
    # user to log in at all - see pyobs-core's specs/design/shared-authz-keycloak.md. Empty
    # disables the gate entirely (every authenticated Keycloak user would be authorized), so
    # this must be set - and the group populated in Keycloak - before deploying with Keycloak
    # login enabled. Per-installation, not fleet-wide (see the individual site's own
    # keycloak-service-topology.md design doc): override via KEYCLOAK_REQUIRED_GROUP.
    "REQUIRED_GROUPS": [g for g in [os.environ.get("KEYCLOAK_REQUIRED_GROUP", "/pyobs-weather")] if g],
}


# try to import a local_settings.py
try:
    from .local_settings import *
except ImportError:
    pass
