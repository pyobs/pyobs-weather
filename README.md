# pyobs-weather

pyobs-weather is an aggregator for data from several weather stations. Rules can be defined for when weather
is considered "good". It provides both a web frontend and an API for access.

## Documentation

Full installation (Docker Compose), configuration (every environment variable), architecture (how
the Django app, Celery, InfluxDB, and the Vue frontend fit together), and REST API reference: see
[`docs/source/`](docs/source/) (built with Sphinx — `cd docs && uv run --with sphinx --with sphinx-rtd-theme make html`).

## Development

```bash
git clone https://github.com/pyobs/pyobs-weather.git
cd pyobs-weather
uv sync --group dev
```

See [`docs/source/development.rst`](docs/source/development.rst) for the full local-dev flow
(SQLite setup, running the Vue frontend's dev server), and
[`docs/source/installation.rst`](docs/source/installation.rst) for the Docker Compose production
setup.

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
