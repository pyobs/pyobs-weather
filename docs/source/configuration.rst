Configuration
#############

All settings are controlled by environment variables — copy ``.env.example`` to ``.env`` and
adjust.

Django
******

``SECRET_KEY`` (default: ``changeme``)
    Django secret key — **change in production**.

``DEBUG`` (default: ``0``)
    Set to ``1`` for development.

``DJANGO_ALLOWED_HOSTS`` (default: ``localhost,127.0.0.1``)
    Comma-separated list of allowed hosts.

``CSRF_TRUSTED_ORIGINS`` (default: ``http://localhost``)
    Comma-separated list of trusted origins.

``ROOT_URL`` (default: ``/``)
    URL prefix the app is served under, if not at the domain root.

``STATIC_ROOT`` (default: ``/static/``)
    Directory for collected static files.


Database
********

``SQL_ENGINE`` (default: ``django.db.backends.postgresql``)
    Database backend.

``SQL_DATABASE``, ``SQL_USER``, ``SQL_PASSWORD``, ``SQL_HOST``, ``SQL_PORT``
    Database connection (defaults: ``postgres`` / ``postgres`` / ``postgres`` / ``db`` /
    ``5432``). ``POSTGRES_DB``/``POSTGRES_USER``/``POSTGRES_PASSWORD`` in ``.env.example`` set
    the same values for the ``db`` container itself under Docker Compose — keep both in sync.


Task scheduling (Celery)
*************************

``CELERY_BROKER_URL`` (default: ``amqp://``)
    RabbitMQ connection string for the Celery broker.

``CELERY_RESULT_BACKEND`` (default: ``rpc://``)
    Where Celery task results are stored.


Sensor history (InfluxDB)
***************************

``USE_INFLUX`` (default: ``1``)
    Store/read sensor history from InfluxDB rather than Postgres.

``INFLUXDB_URL``, ``INFLUXDB_TOKEN``, ``INFLUXDB_ORG`` (default URL: ``http://localhost:8086``)
    Connection to the InfluxDB instance.

``INFLUXDB_BUCKET`` (default: ``weather``), ``INFLUXDB_BUCKET_5MIN`` (default: ``weather_average``)
    Buckets for raw readings and 5-minute averages respectively.

``INFLUXDB_MEASUREMENT_AVERAGE`` (default: ``average``)
    Name of the synthetic "Average" station/measurement (see :doc:`architecture`).


Site
****

``OBSERVER_NAME`` (default: ``MONET/N @ McDonald Observatory`` — set this)
    Display name for the site, used as the default ``WINDOW_TITLE`` too.

``OBSERVER_LONGITUDE``, ``OBSERVER_LATITUDE``, ``OBSERVER_ELEVATION`` (defaults: McDonald Observatory's coordinates — set these)
    Site location, used by the built-in "Observer" station to compute solar altitude (see
    :doc:`stations/index`).

``WINDOW_TITLE`` (default: ``Weather at <OBSERVER_NAME>``)
    Browser tab title / frontend header.

``WEATHER_SENSORS`` (default: ``temp,humid,press,windspeed,winddir,rain,skytemp,sunalt``)
    Comma-separated sensor-type codes shown as current values (``/api/current/``,
    ``/api/config/``).

``WEATHER_PLOTS`` (default: ``temp,humid,press,windspeed,winddir,rain,skytemp``)
    Comma-separated sensor-type codes plotted in the history view.

Beyond the environment, weather stations and their evaluators are configured through the Django
admin panel, not env vars or a config file — see :doc:`architecture`.
