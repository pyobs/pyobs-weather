# pyobs-weather

pyobs-weather is an aggregator for data from several weather stations. Rules can be defined for when weather
is considered "good". It provides both a web frontend and an API for access.


## Documentation

See the documentation at https://pyobs.github.io/.


## Deployment with Docker

The easiest way to deploy is with the included `docker-compose.yml`, which sets up all required services:
PostgreSQL, RabbitMQ, Celery, nginx, and the weather app itself.

**1. Create a `.env` file** from the provided example and fill in your values:

    cp .env.example .env

At minimum set `SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and the database/InfluxDB credentials.
See `.env.example` for all available options including the observer location.

**2. Start all services:**

    docker-compose up -d

**3. Initialise the database** (only needed on first run):

    docker-compose exec weather uv run ./manage.py initweather
    docker-compose exec weather uv run ./manage.py createsuperuser

The web frontend is accessible at http://localhost/ and the admin panel at http://localhost/admin.

The `nginx.conf` in this repository is used automatically by the nginx container — no manual configuration needed.


## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

    uv sync --group dev

Copy `.env.example` to `.env`, set `SQL_ENGINE=django.db.backends.sqlite3` and `SQL_DATABASE=db.sqlite3`
for a local SQLite database, then load the environment and run migrations:

    set -a && source .env && set +a
    uv run ./manage.py migrate
    uv run ./manage.py runserver


## Backup and restore

Back up the full weather configuration (excluding raw sensor readings):

    docker-compose exec weather uv run ./manage.py dumpdata --indent 2 weather --exclude weather.value > weather.json

To include sensor readings as well:

    docker-compose exec weather uv run ./manage.py dumpdata --indent 2 weather > weather.json

Restore on a fresh setup:

    docker-compose exec weather uv run ./manage.py loaddata weather.json


## Changelog

#### version 1.2 (2024)
- Switched from Poetry to uv
- Upgraded Django 3.2 → 5.2 LTS
- Replaced Redis with RabbitMQ as message broker
- Configuration moved from `local_settings.py` to environment variables

#### version 1.0 (2020-11-23)
- Initial release

#### version 1.1 (2020-11-24)
- Added footer to page
- Exclude average station from status evaluation
- Logging current good/bad weather status
- Added plot for solar elevation and good weather for last 24h

#### version 1.1.1 (2020-11-24)
- Fixed bug with update of plots
