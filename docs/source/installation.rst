Installation
############

Docker Compose is the supported way to run *pyobs-weather* in production. The repository's
`docker-compose.yml
<https://github.com/pyobs/pyobs-weather/blob/develop/docker-compose.yml>`_ sets up everything
needed:

- **weather** — the app itself (``ghcr.io/pyobs/pyobs-weather:latest``).
- **celery** — same image, runs the scheduled station-polling tasks (``celery -A pyobs_weather
  worker -B --scheduler django``).
- **rabbitmq** — Celery's message broker.
- **db** — PostgreSQL, for station/evaluator configuration and the good/bad weather log.
- **nginx** — serves static files and proxies to **weather**.

Sensor history is stored in InfluxDB (``USE_INFLUX=1``), which isn't part of this
``docker-compose.yml`` — point ``INFLUXDB_URL`` at an existing instance, or add one yourself.

Setup::

    git clone https://github.com/pyobs/pyobs-weather.git
    cd pyobs-weather
    cp .env.example .env
    # edit .env: at minimum SECRET_KEY, DJANGO_ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS,
    # the database/InfluxDB credentials, and OBSERVER_*
    docker-compose up -d

Then initialise the database (only needed on first run) — this seeds the built-in "Current",
"Average", and "Observer" stations (see :doc:`configuration`)::

    docker-compose exec weather uv run ./manage.py initweather
    docker-compose exec weather uv run ./manage.py createsuperuser

The web frontend is at ``http://localhost/`` and the admin panel at ``http://localhost/admin``.
The included ``nginx.conf`` is used automatically — no manual configuration needed.

See :doc:`configuration` for every setting ``.env`` can carry, and :doc:`development` for running
it locally without Docker.
