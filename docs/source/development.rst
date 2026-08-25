Development
###########

This project uses `uv <https://docs.astral.sh/uv/>`_ for dependency management::

    git clone https://github.com/pyobs/pyobs-weather.git
    cd pyobs-weather
    uv sync --group dev

Copy ``.env.example`` to ``.env``, set ``SQL_ENGINE=django.db.backends.sqlite3`` and
``SQL_DATABASE=db.sqlite3`` for a local SQLite database, then load the environment and run
migrations::

    set -a && source .env && set +a
    uv run ./manage.py migrate
    uv run ./manage.py runserver

The web frontend is a Vue app in ``frontend-vue/`` (built with Vite). For development, run its dev
server alongside Django::

    cd frontend-vue
    npm install
    npm run dev

The dev server proxies ``/api``, ``/admin``, and ``/static`` to ``http://localhost:8000``. For a
production build (served by Django via the ``dist/`` output)::

    cd frontend-vue
    npm run build

Backup/restore the full weather configuration (excluding raw sensor readings, which live in
InfluxDB — see :doc:`architecture`)::

    uv run ./manage.py dumpdata --indent 2 weather --exclude weather.value > weather.json
    uv run ./manage.py loaddata weather.json
