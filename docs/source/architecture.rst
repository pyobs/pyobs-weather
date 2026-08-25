Architecture
############

*pyobs-weather* is a stand-alone Django service (no ``pyobs-core`` dependency, not part of an
XMPP fleet), made up of four pieces:

- **Django app** (``pyobs_weather``) — the admin panel (where stations and evaluators are
  configured, not via env vars — see :doc:`configuration`), the REST API (:doc:`api`), and the
  scheduling glue.
- **Celery + RabbitMQ** — each configured station is polled on its own crontab/interval by a
  Celery beat schedule; each poll writes new sensor readings and re-runs evaluators.
- **PostgreSQL** — station/evaluator/sensor-type configuration, and the good/bad weather change
  log (``GoodWeather``, exposed at ``/api/history/goodweather/``).
- **InfluxDB** — sensor value history (raw readings + 5-minute averages), read by
  :doc:`stations/index`. Historical plots and the ``/api/history/<type>/`` endpoint read from
  here, not Postgres.

A **station** (:doc:`stations/index`) is a pluggable Python class polling one real or synthetic
data source; adding one in the admin panel just needs a station code, a class, and a
polling schedule. Every station's readings feed into two built-in synthetic stations:
"Average" (5-minute averages across all stations) and "Current" (latest averaged values — what
``/api/current/`` serves). An **evaluator** (:doc:`evaluators/index`) attaches to a sensor and
decides whether its current value counts as "good"; a sensor with no evaluator is neutral (not
counted against "good" at all).

The **frontend** is a Vue SPA (``frontend-vue/``), served as static files by Django/nginx in
production, that reads everything through the REST API in :doc:`api` — there's no server-rendered
page for the live weather view. External consumers (telescope-control software deciding whether
it's safe to observe) use the same REST API.
