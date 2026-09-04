# Plan: login-gated historic data CSV export

Issues: #6 (originally "see plots for previous nights"; rescoped 2026-09-04 to a data export now
that login exists). Depends on #33/`2026-09-02-keycloak-login.md` (done, `/api/me/` +
`request.user.is_authenticated` already available). Repo: pyobs-weather only.

Status: implemented, PR open. Sections 1-3 done 2026-09-04.

The original 2020 ask ("plots for previous nights") predates Keycloak login. With login now in
place (`2026-09-02-keycloak-login.md`), the more useful version of this is a login-gated raw-data
export: pick a station and a date range, download a CSV. Not a chart.

## 1. Data shape

- One selected station per download (not multi-station-in-one-file — see §6).
- Station choices: any `Station` with `active=True` and `history=True` — same filter
  `history()`/`history_types()` already apply in `pyobs_weather/api/views.py`. Include the
  synthetic `average` station: confirmed live on MONET it does have `history=True` (its `rain`
  sensor's evaluator-band data shows up via `history()`'s `areas` path, which only fires for
  sensors that pass the same `station__history=True, station__active=True` filter this plan
  reuses) — it's a real, useful single-file whole-site export, not a special case to exclude.
  `observer` (Tim confirmed: `history=False` — it's just solar elevation, nothing to export) is
  correctly excluded by the same filter.
- Columns in the CSV: `timestamp`, then `<sensor_type_code>_mean`, `_min`, `_max` for each
  `Sensor` where `station=<selected>, active=True` — same three `agg_type` values
  `read_sensor_values()` already reads (`pyobs_weather/weather/influx.py`), just reshaped **per
  station** instead of **per sensor type across stations**.
- Round exported values to 2 decimals (raw Influx values come back at full float precision, e.g.
  `7.322222222222224` — confirmed live on MONET's `temp` history).
- Leave a cell blank for a timestamp/sensor combo with no data rather than erroring — confirmed
  live that a real station can be fully offline (`suth` at MONET currently returns `null` for
  every sensor).
- **Scope strictly through the Django `Station`/`Sensor` tables — never a raw Influx query against
  the bucket.** Verified directly against MONET's `weather_average` bucket (via `influx` CLI on
  the `ms` host): it also holds measurements with no matching `Station` row at all (`monet` —
  telescope M1/M2/flange structure temperatures, written by an unrelated system, actively
  updating). Going through `Sensor.objects.filter(station__code=...)` excludes those automatically;
  a "just query the bucket for this measurement name" shortcut would not, and would silently work
  today only because no `Station.code` happens to collide with a non-weather measurement.
- No new aggregation/bucket-size decision needed: InfluxDB already only retains 5-minute averages
  long-term (confirmed live: the raw, undownsampled `weather` bucket has 48h retention on MONET;
  `weather_average` is the only bucket with real history — infinite retention, oldest confirmed
  point 2023-07-04 for `thiesws`/`temp`). 5-min is both the default and the only historically
  available granularity.

## 2. Backend

New endpoint, e.g. `GET /api/history/export/<station_code>/?start=&end=`, in
`pyobs_weather/api/views.py` + `pyobs_weather/api/urls.py`:

- [x] `request.user.is_authenticated` required; anonymous → `401`. No frontend route-guard
      needed as the primary control — this repo has no route-guard mechanism yet, and the API
      check is what's actually secure against someone hitting the URL directly.
- [x] `Station.objects.get(code=station_code, active=True, history=True)`, 404 if not found/not
      eligible.
- [x] `start`/`end` query params, same `dateutil.parser.parse` handling `history()` already uses;
      both required, `400` if either is missing — no "last 24h" implicit default the way
      `history()` has, this is an explicit export, not a live plot.
- [x] For each `Sensor.objects.filter(station=station, active=True)`: `read_sensor_values(sensor,
      start, end, agg_type=...)` for `mean`/`min`/`max`. Deviated from "zipped by timestamp like
      `history()` already does" above: merged into a `{timestamp: value}` dict per column instead
      of positional `zip()` — `history()`'s zip assumes `mean`/`min`/`max` come back the same
      length and order, which is fine for a live plot but not safe for an export where a gap in
      one aggregate shouldn't misalign every column after it.
- [x] Stream the response (`django.http.StreamingHttpResponse` + `csv.writer`, not a
      fully-materialized string/`JsonResponse`) — a full-history single-station export can be a few
      hundred thousand rows (see §1's 2023-07-04 depth check), so this isn't reliably a "one
      night" payload.
- [x] `Content-Disposition: attachment; filename="<station_code>_<start>_<end>.csv"`.
- [x] `stations_list()`/`/api/stations/` now also returns `history`, for the frontend's station
      picker (§3) — that endpoint had no frontend consumer before this, so widening its response
      shape is risk-free.

## 3. Frontend

New view (e.g. `HistoryDownloadView.vue`) + route in `frontend-vue/src/router/index.ts`:

- [x] Sidebar `RouterLink` only rendered `v-if="me?.authenticated"`, alongside the existing
      Overview/Sensors links in `App.vue` (mirrors the existing login/logout link pattern, driven
      by the existing `/api/me/` — no new auth plumbing).
- [x] Station `<select>` populated from `/api/stations/`, filtered client-side to `history: true`.
- [x] Start/end date inputs (native `<input type="date">`, defaulted to the last 7 days on mount).
- [x] Download button: `fetch()` the export endpoint, save the blob (`URL.createObjectURL` +
      synthetic `<a download>`), filename read back from the response's `Content-Disposition`.
- [x] Visiting the route directly while logged out: the form is replaced entirely by a "Log in to
      download historic data." message + login link, driven by the same shared `me` ref `App.vue`
      already loads — no duplicate auth fetch, no route guard needed for v1.
- [x] `historyExportUrl()` (pure URL-building helper, `api/client.ts`) unit-tested in
      `client.spec.ts`; the login-gate + happy-path download flow (including the browser actually
      saving a file with the right name) covered end-to-end in `e2e/app.spec.ts` against a mocked
      API, run via Playwright against both desktop and mobile viewports.

## 4. Review follow-up (2026-09-04)

Addressed from the PR review (all landed on the feature branch):

- End date is now treated as inclusive for a bare `YYYY-MM-DD` (InfluxDB's `range()` stop is
  exclusive; without the bump, `end=2026-01-02` silently excluded that whole day).
- `dateutil.parser.parse()` failures now return `400` instead of an unhandled `ParserError`
  bubbling up as a `500`; `end <= start` is rejected too.
- Timezone-aware input is normalized to naive UTC instead of having its offset silently dropped
  by `read_sensor_values()`'s `strftime('...Z')`.
- Exported values formatted with a fixed `.2f` instead of `round()`, for consistent decimal
  places.
- `HistoryDownloadView.vue`'s login prompt no longer shows a dead Keycloak link when
  `config.keycloak_enabled` is false; a `401` mid-session now flips the view back to the
  logged-out state instead of leaving a stale form up; station `<select>` sorted by name.

Left as noted-but-not-done, per the review's own "worth considering"/nits framing rather than
blocking: the CSV headers still don't carry units, the response still gathers all Influx queries
eagerly before the stream starts (documented in `_EchoBuffer`'s docstring, not changed), and
`Sensor` still has no DB-level `(station, type)` uniqueness constraint (documented in a comment
instead — a real fix would be a migration, out of scope here).

## 5. Verification

- Backend: `manage.py test pyobs_weather.api` — 13 tests (11 for this endpoint, covering 401/400/
  404, the happy path with formatting + blank-cell handling, the empty-range/header-only case,
  unparseable dates, `end <= start`, the inclusive-bare-end-date bump, and timezone normalization),
  plus the existing 2 `/api/me/` tests. Run against sqlite (`SQL_ENGINE=django.db.backends.sqlite3`
  ), since the repo's Postgres isn't set up locally.
- Frontend: `vue-tsc -b` clean, `vite build` clean, `vitest run` (35 tests, +2 new for
  `historyExportUrl`), `playwright test` (13 passed/1 skipped across desktop+mobile, +5 new for
  this feature, one of them a real end-to-end download through a headless browser).
- **Found, not fixed (pre-existing, unrelated):** `manage.py test` (full suite, no app filter)
  fails to even import `pyobs_weather.weather.stations` — its `__init__.py` unconditionally
  imports `mcdtelnet.py`, which does `from telnetlib import Telnet`; `telnetlib` was removed in
  Python 3.13, which is what's installed in `.venv` and within this repo's own
  `requires-python = ">=3.12"`. Worked around in this endpoint's tests by giving the test `Station`
  fixture a tiny standalone handler class instead of going through that package (see
  `_TestStationHandler` in `pyobs_weather/api/tests.py`) rather than fixing the underlying import.
  Also noticed: the pinned `black` version in `pyproject.toml` can't run under this `.venv`'s
  `click` version either (`ImportError: cannot import name '_unicodefun'`) — formatting was
  checked with a standalone `black` install instead. Neither is this plan's job to fix.

## 6. Not in this plan

- Multi-station CSV in one file (comparing stations side by side) — single-station export only;
  revisit if that turns out to be the actual use case rather than an assumption.
- Custom aggregation windows/bucket sizes — 5-minute is both the default and the only granularity
  that exists historically (see §1).
- Plots for historic dates — the original 2020 framing; this plan replaces it with a raw-data
  export instead, per the 2026-09-04 rescoping.
- A generic route-guard mechanism for login-gated pages — this is the first one; a real guard
  abstraction can wait until there's a second.
