# Development notes

## Migrating off InfluxDB to PostgreSQL

### Motivation

InfluxDB is currently used as a second datastore alongside the primary PostgreSQL
database (which already holds all Django models: `Station`, `Sensor`, `SensorType`,
`Value`, `Evaluator`, `GoodWeather`, celery-beat schedules, ...). Influx has been
causing operational trouble and is being dropped. All time-series data will move
into two new fixed-column tables in the existing PostgreSQL instance, removing a
whole datastore (and its client library, auth tokens, bucket/retention config, and
the external Flux aggregation task that currently produces the 5-minute buckets)
from the stack.

### Current state (for reference)

- `pyobs_weather/weather/influx.py` wraps `influxdb_client` with 4 functions:
  `read_sensor_value` (latest value, from bucket `INFLUXDB_BUCKET`), `read_sensor_values`
  (ranged, aggregated, from bucket `INFLUXDB_BUCKET_5MIN`, filtered by `agg_type` in
  `{mean, min, max}`), `write_sensor_value`, `write_sensor_values`.
- Each station is an Influx *measurement* (`station.code`); each sensor type is a
  *field* (`sensor.type.code`) on that measurement. This is a narrow/tall layout.
- The 5-minute mean/min/max rollup bucket (`INFLUXDB_BUCKET_5MIN`) is **not**
  produced by any code in this repo — it's an InfluxDB task/Flux script configured
  out-of-band directly against the Influx server. This logic needs to be
  reimplemented as a Celery task as part of this migration.
- `Sensor`/`SensorType` are still Django/Postgres models — only the actual
  numeric readings live in Influx. `Value` (a Django model) exists but is
  effectively dead when `USE_INFLUX=1` (the default); it's only used when Influx
  is disabled, and via `dump_weather` / `initweather` management commands.
- The "average" station (code from `INFLUXDB_MEASUREMENT_AVERAGE`, a Django
  `Station` row) is a virtual station computed by `stations/average.py`, which
  reads the latest value of every real sensor and writes an averaged value back
  through the same `write_sensor_value` path.
- Callers of the influx module: `weather/stations/station.py`,
  `weather/stations/average.py`, `api/views.py` (`station_detail`,
  `sensor_detail`, `current`, `history`, `sensors`), `weather/apps.py` (client
  init on startup).

### Target schema

Two fixed-column tables, both keyed on `(time, station)`, one row per station per
timestamp (wide layout — one column per sensor type instead of Influx's
measurement+field layout). Column set is exactly the current `SENSOR_TYPES` in
`weather/stations/station.py` (`temp`, `humid`, `dewpoint`, `press`, `winddir`,
`windspeed`, `particles`, `rain`, `skytemp`, `skymag`, `sunalt`).

**Raw incoming readings** — one row per station update, at whatever cadence that
station's crontab/interval schedule uses (10s–30s typically):

```sql
CREATE TABLE weather_readings (
    time         TIMESTAMPTZ NOT NULL,
    station      TEXT NOT NULL,
    temp         DOUBLE PRECISION,
    humid        DOUBLE PRECISION,
    dewpoint     DOUBLE PRECISION,
    press        DOUBLE PRECISION,
    winddir      DOUBLE PRECISION,
    windspeed    DOUBLE PRECISION,
    particles    DOUBLE PRECISION,
    rain         DOUBLE PRECISION,
    skytemp      DOUBLE PRECISION,
    skymag       DOUBLE PRECISION,
    sunalt       DOUBLE PRECISION,
    PRIMARY KEY (time, station)
);
```

**5-minute aggregates** — replaces the old Flux rollup task. One row per
`(time bucket, station, agg_type)`, mirroring the `agg_type` filter that
`read_sensor_values` already does today, so the read-path query shape barely
changes:

```sql
CREATE TABLE weather_averages (
    time         TIMESTAMPTZ NOT NULL,
    station      TEXT NOT NULL,
    agg_type     TEXT NOT NULL,   -- 'mean' | 'min' | 'max'
    temp         DOUBLE PRECISION,
    humid        DOUBLE PRECISION,
    dewpoint     DOUBLE PRECISION,
    press        DOUBLE PRECISION,
    winddir      DOUBLE PRECISION,
    windspeed    DOUBLE PRECISION,
    particles    DOUBLE PRECISION,
    rain         DOUBLE PRECISION,
    skytemp      DOUBLE PRECISION,
    skymag       DOUBLE PRECISION,
    sunalt       DOUBLE PRECISION,
    PRIMARY KEY (time, station, agg_type)
);
CREATE INDEX weather_averages_station_time_idx ON weather_averages (station, time);
```

`time` in `weather_averages` is the start (or midpoint — pick one, see open
questions) of the 5-minute bucket, truncated with `date_bin('5 minutes', ...)` /
`date_trunc`-style alignment so buckets line up across stations.

Both tables are represented as ordinary **managed Django models** (`WeatherReading`,
`WeatherAverage` in `weather/models.py`), keeping table creation in the normal
Django migration flow. This project is already on Django 5.2, which added
`models.CompositePrimaryKey` — so the models can use the *exact* composite
primary key shown above (`pk = models.CompositePrimaryKey("time", "station")`,
resp. `("time", "station", "agg_type")`) instead of a surrogate `id` +
`UniqueConstraint`. That composite pk doubles as the unique index the write
path's upserts key off: `QuerySet.bulk_create(..., update_conflicts=True,
unique_fields=[...], update_fields=[...])` (Django ≥4.1) instead of hand-written
`INSERT ... ON CONFLICT` SQL. Add a secondary index on `(station, time)` (and
`(station, agg_type, time)`) for the read path, since the pk's leading column is
`time`, not `station`.

### Write path

Replace `influx.write_sensor_value` / `write_sensor_values` with equivalent
functions (new module, e.g. `weather/timeseries.py`) that upsert into
`WeatherReading`:

- `write_sensor_value(sensor, time, value, station=None)`: upsert a single-column
  update — `bulk_create([WeatherReading(time=time, station=code, **{field: value})],
  update_conflicts=True, unique_fields=["time", "station"], update_fields=[field])`.
- `write_sensor_values(time, station, values)`: same, but with every field in
  `values` set on the one row, and all of them in `update_fields`.

Both keep their current call signatures so `stations/station.py` and
`stations/average.py` need no changes beyond the import.

### Aggregation job (new)

A new Celery beat task (e.g. `weather.tasks.aggregate_5min`), scheduled every 5
minutes, that:

1. Computes the most recently *completed* 5-minute window (`[bucket_start,
   bucket_start + 5m)`).
2. For every distinct `station` with rows in `weather_readings` in that window,
   runs one aggregate query (`AVG`/`MIN`/`MAX` per sensor column, grouped by
   station) — a single `GROUP BY station` query per agg_type, not per-sensor, so
   it's 3 queries total regardless of station/sensor count.
3. Upserts the three resulting rows (`mean`/`min`/`max`) per station into
   `weather_averages` via the same `bulk_create(update_conflicts=True, ...)`
   pattern.

This replaces the out-of-band Influx task, and unlike that task, is now visible,
versioned, and testable in this repo.

### Read path

- `read_sensor_value(sensor)` → `WeatherReading.objects.filter(station=sensor.station.code).order_by("-time").values("time", sensor.type.code).first()`,
  reshaped to the existing `{"time": ..., "value": ...}` return shape.
- `read_sensor_values(sensor, start, end, agg_type)` → `WeatherAverage.objects.filter(station=..., agg_type=agg_type, time__range=(start, end)).order_by("time").values("time", sensor.type.code)`,
  reshaped the same way `history()` in `api/views.py` expects.

Both keep their existing signatures, so `api/views.py` and `stations/average.py`
need only an import-path change, not logic changes.

### Retention / pruning

- `weather_readings` (raw): prune rows older than **2 days** — mirrors the
  short-lived raw bucket Influx had, and is comfortably more than the `history()`
  API's default 1-day window and the `Average.update()` 10-minute staleness check.
- `weather_averages` (5-min rollups): kept much longer (proposed default: **1
  year**) since these are cheap (1/300th the row rate of raw) and back the
  frontend history charts.
- Implement as one Celery beat task per table (or one task, two deletes),
  scheduled hourly, e.g. `WeatherReading.objects.filter(time__lt=now - 2 days).delete()`.
- Make both windows configurable via settings/env (e.g.
  `WEATHER_RAW_RETENTION_DAYS=2`, `WEATHER_AVERAGE_RETENTION_DAYS=365`), following
  the existing `os.environ.get(...)` pattern in `settings.py`, so they can be
  tuned in production without a code change.
- Table growth check: at one raw row per station per ~10–30s, a handful of
  stations is on the order of 10-50k rows/day — pruned at 2 days this stays tiny.
  Revisit if the station count grows a lot.

### Backfill from InfluxDB

Since existing history should be preserved, add a one-off management command
(e.g. `manage.py migrate_influx_history`) that:

1. For each `Station`, queries Influx's raw bucket (`INFLUXDB_BUCKET`), and for
   each `agg_type` in `{mean, min, max}`, the 5-minute bucket
   (`INFLUXDB_BUCKET_5MIN`), then bulk-inserts into `weather_readings` /
   `weather_averages` respectively.
2. Queries **all fields for a station in one shot** with Flux's `pivot()`
   (`|> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")`),
   turning Influx's narrow measurement+field rows into the same wide
   one-row-per-timestamp shape the new tables use — this is a big improvement
   over the current `influx.py` read functions, which fetch one field at a time
   per sensor; a naive per-sensor backfill would be ~11x more queries than
   necessary.
3. Chunks the time range per query (e.g. day-sized chunks for the raw bucket,
   month-sized for the 5-min bucket — raw is ~300x denser) to keep each Flux
   query's result set bounded, regardless of how many years are being pulled.
4. Upserts via `bulk_create(update_conflicts=True, unique_fields=[...],
   update_fields=[...])` (same mechanism as the live write path, see above) so
   the whole command is idempotent/resumable — safe to re-run, or to interrupt
   and continue from a later `--start`, if a multi-year pull against a
   possibly-flaky Influx instance needs retries.
5. Runs once, manually, against the still-running Influx instance *before* it's
   decommissioned — this command (and the `influxdb_client` dependency) can be
   deleted once the backfill is done and verified.

Proposed CLI shape: `--start`/`--end` (ISO8601, default start far enough back to
cover all real data, end defaults to now), `--station` (default: all), separate
`--raw-chunk-days`/`--average-chunk-days`, `--skip-raw`/`--skip-averages`, and a
`--batch-size` for the `bulk_create` calls.

Open question: how far back does history actually need to go? Worth checking
current Influx retention policies on the bucket before assuming "all of it" —
there's a chance the raw bucket already only holds a few days and only the 5-min
bucket has long history, which would simplify step 1 a lot.

Caveat to watch for during backfill: `pivot()` groups fields into one row only
when they share the *exact* same `_time`. The live write path already writes all
fields of a reading together under one timestamp (`write_sensor_values`), so
this should hold for most data — but any historical `write_sensor_value` calls
that wrote fields separately (slightly different timestamps) would pivot into
sparse, mostly-null rows instead of merging. Worth spot-checking a sample
station's raw data for this before trusting the backfill counts.

### Rollout plan

1. Add `WeatherReading` / `WeatherAverage` models + migration (additive, no
   behavior change yet).
2. Add `weather/timeseries.py` with the write/read functions above; add the
   `aggregate_5min` and retention/pruning Celery beat tasks.
3. Switch `stations/station.py`, `stations/average.py`, `api/views.py` to import
   from `timeseries.py` instead of `influx.py`. Remove the `USE_INFLUX` branch in
   `weather/apps.py` and the dead `USE_INFLUX` check in `Value.save()`
   (`models.py:140` — `Value` becomes fully unused at this point, consider
   dropping it and the `dump_weather` command, or repointing `dump_weather` at
   the new tables if it's still wanted).
4. Run the backfill command against the still-live InfluxDB instance.
5. Verify frontend history charts and `current`/`sensors`/`station_detail` API
   endpoints match pre-migration output for a sample station.
6. Remove `influx.py`, the `influxdb_client` dependency, `INFLUXDB_*` /
   `USE_INFLUX` settings and env vars, and decommission the InfluxDB
   server/container.
7. Rename `INFLUXDB_MEASUREMENT_AVERAGE` → something like `AVERAGE_STATION_CODE`
   while touching that code — it's just the code of the virtual "average"
   `Station` row and has nothing to do with Influx measurements anymore.

### Open questions

- Exact historical range to backfill (see above) — depends on current Influx
  retention config, need to check before writing the backfill command.
- Bucket timestamp convention for `weather_averages.time`: start vs. midpoint of
  the 5-minute window (needs to match whatever the *existing* Flux task used, so
  backfilled and newly-computed rows line up).
- Whether `particles`/`rain`/etc. that aren't plain continuous measurements need
  a different aggregation (e.g. `rain` looks boolean-ish per `SENSOR_TYPES`
  unit `""`) — confirm `MAX`/`MIN`/`AVG` are all meaningful for every column, or
  whether some should just carry `mean` forward for `min`/`max` too.
