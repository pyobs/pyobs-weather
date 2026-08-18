# Plan: Modernize frontend — Vue 3 + Vite + TypeScript, rework plots

Status: planned — two open questions below unresolved.

Issues: #25

## Problem

pyobs-weather's web frontend is the outlier in the pyobs web ecosystem. Every other pyobs web
project (pyobs-web-client, pyobs-web-admin) is Vue 3 + Vite + TypeScript + Bootstrap 5;
pyobs-weather is server-rendered Django templates plus a hand-written jQuery/Chart.js/moment.js
stack with no build step, no package.json, no type checking, and no frontend tests:

- `pyobs_weather/frontend/templates/` — `base.html`, `index.html`, `sensors.html`,
  `documentation.html`.
- `pyobs_weather/frontend/static/frontend/js/app.js` (450 lines) — overview-page logic: builds
  Chart.js plots (`create_plot`/`plot`/`plot_dict`), polls `/api/current/` every 10s, draws the
  day/night timeline onto a raw `<canvas>`, and renders the good-weather history chart. All jQuery
  plus global functions.
- `app-sensors.js` — the one piece of Vue already in the repo, and it's Vue 2 (`vue.min.js`,
  `[[ ]]` delimiters) polling `/api/sensors/` every 10s.
- Vendored, un-managed libraries in `static/frontend/js/vendor/` (chart.min.js,
  chartjs-plugin-annotation, chartjs-adapter-date-fns, jquery, moment, vue.min.js).

The backend is not the problem: `pyobs_weather/api/` already exposes everything the frontend needs
as JSON (`/api/current/`, `/api/stations/`, `/api/stations/<code>/`, `/api/stations/<code>/<sensor>/`,
`/api/sensors/`, `/api/history/`, `/api/history/<type>/`, `/api/history/goodweather/`,
`/api/timeline/`). The gap is purely the presentation layer.

## Scope

Frontend-only. Keep `pyobs_weather/api/`, `pyobs_weather/weather/` (stations, evaluators), and the
Celery/InfluxDB plumbing as-is. Replace the server-rendered templates + jQuery/Chart.js frontend
with a Vue 3 + Vite + TypeScript + Bootstrap 5 single-page app consuming the existing JSON API,
matching pyobs-web-client's conventions (Vite, vue-router, bootstrap + bootstrap-icons, vitest,
playwright). Rework the sensor plots as part of this rather than porting them verbatim.

## What the current frontend actually does (nothing here may be silently dropped)

Three Django-served pages, each its own template + JS:

1. **Overview `/`** (`index.html` + `app.js`):
   - "Current" column: per-sensor latest value (color-coded green/red from `/api/current/`'s
     per-type `good`), plus an overall GOOD/BAD line and the read time. The set of sensors shown is
     server-rendered (`value_types`).
   - Day/night timeline: a 20px canvas strip showing sunset → dusk → night → dawn → sunrise with a
     red "now" marker, from `/api/timeline/`.
   - "Plots for last 24h": a good-weather history chart (solar elevation over 24h with green/red
     good/bad bands, from `/api/history/goodweather/`) plus one Chart.js line chart per `plot_types`
     sensor type (from `/api/history/<type>/`).
   - The per-type history chart renders, per non-average station, three datasets (mean/min/max,
     min/max fanned with fill), plus horizontal annotation boxes from the evaluators' `areas()`
     (danger red, warning yellow).
2. **Sensors `/sensors/`** (`sensors.html` + `app-sensors.js`): a live table of every active sensor
   (station, sensor, value+unit, good, since, delay comment) from `/api/sensors/`. Kept as its own
   page in the rework (see "Target layout").
3. **Documentation `/docs/`** (`documentation.html`): static content, no JS. **Dropped** — not
   migrated.

## Target layout

Sidebar-driven, matching the sibling clients' sidebar-nav shape:

- A **sidebar** is filled with the current values — one entry per sensor type from
  `config.value_types` (label, value, unit, good/bad color), plus the overall GOOD/BAD banner and
  read time, all from `/api/current/` (~10s poll). This replaces the overview page's current
  "Current" column.
- **Tapping/clicking a current value expands the per-station breakdown in place** (accordion,
  not hover): that sensor type's per-station values, good/bad, `since`, and delay comment, from
  `/api/sensors/` filtered by `type_code`. A quick shortcut, not a replacement for the full page.
- A dedicated **Sensors page** (own route + sidebar nav entry) keeps the full live table of every
  active sensor, as today.
- The main content area keeps the day/night timeline and the 24h plots (good-weather history plus
  the per-type sensor charts).

Two views, then: Overview (timeline + plots, sidebar current values) and Sensors (the full table).
The Documentation page is dropped. Whether the sidebar's current values live on both views or only
the Overview is an open question below.

## Mobile conventions (from the sibling projects)

The other pyobs web projects treat mobile as first-class, and none of them use hover for
disclosure — hover has no touch equivalent. `pyobs-archive` and `pyobs-web-admin` share the same
Bootstrap 5 shell (archive's `templates/base.html` is the origin; web-admin's mirrors it) and that
shell is the reference to mirror here. (`pyobs-robotic-backend` is still the older Django-template +
jQuery style, same generation as the current weather frontend — not a mobile reference.)

- **Sidebar as an off-canvas drawer on mobile**: fixed sidebar on desktop (`width:240px`), on
  `≤991px` it's a `280px` drawer translated off-screen and slid in via a hamburger button plus a
  backdrop overlay (`toggleSidebar()`). Close on nav-link tap.
- **No hover-only interactions** — anything discoverable is tap/click, with expand-in-place
  (accordion rows, `data-bs-toggle="collapse"`) rather than popovers/modals. pyobs-web-admin's
  design index states the convention explicitly: "no modals anywhere... inline expand-in-place
  confirms... for mobile-friendliness."
- **Light/dark theme via `data-bs-theme`** + `localStorage` persistence, with a set of
  `--pyobs-*` surface tokens — part of the shared shell, adopt it rather than hardcoding colors.
- **`.main-content { min-width: 0 }`** on the flex child, so wide content scrolls internally
  (`table-responsive`) instead of overflowing the viewport.
- **Wide tables** use `table-responsive` + `text-nowrap` cells, not smaller text.
- **Buttons collapse to icon-only** on mobile (`d-none d-md-inline`).
- Every page verified at a 390px viewport with no horizontal overflow — that's the standard the
  sibling clients' own plans hold themselves to.

Apply all of the above here: sidebar drawer, tap-to-expand sensor breakdown, `min-width: 0` +
`table-responsive` for anything tabular, theme tokens, and a 390px verification pass. No hover-only
paths.

## Server-rendered context is a real dependency, not just templates

The overview page depends on context only Django can compute today, which a Vue SPA won't get for
free. `OverView.get_context_data` (`frontend/views.py:13`) computes the sensor types to show under
"Current" (`value_types`), which sensor types get a plot (`plot_types`), the site name, and the
observer location formatted as strings — and every AJAX call in `app.js`/`app-sensors.js` prefixes
`rootURL`, which is injected as a page global. Two options, decide which:

- add a small config endpoint (e.g. `/api/config/`) returning `site`/`title`/`root_url`/
  `value_types`/`plot_types`/`location`, or
- hardcode a client-side equivalent (worse: duplicates `settings.WEATHER_SENSORS`/`WEATHER_PLOTS`
  and the astropy location formatting in the frontend).

Leaning config endpoint: it's ~20 lines in `api/views.py` and keeps the SPA schema-driven, matching
how the sibling clients pull config rather than hardcode it.

## Open questions (decide before implementing)

1. **Repo layout: Vue app in this repo vs a separate `pyobs-weather-client` repo.** The issue leans
   "separate Vue app the way pyobs-web-client does", but pyobs-web-client is a generic client for
   any pyobs-core fleet over XMPP — worth its own repo. This UI is specific to pyobs-weather's own
   Django API and is deployed by the same `docker-compose.yml`/`nginx.conf`. Recommendation: keep
   the Vue app in this repo (a `frontend-vue/` or similar tree built by Vite into the Django static
   path), not a new repo — the two-repo deployment dance isn't justified for a single-purpose UI
   whose API lives here. Counter-argument (favoring a split): a fresh Vite repo is cleaner than a
   Vite tree inside a Django repo, and it matches the established pyobs-web-client precedent. Not
   decided either way here.
2. **Charting library.** The sensor plots need three things a plain `<canvas>` time-series doesn't
   give for free: horizontal area annotations (evaluator `areas()`), min/max fanning with fill, and
   a time axis — all of which Chart.js already does (chartjs-plugin-annotation, fill, time scale).
   pyobs-web-client hand-rolled its `TimeSeriesChart.vue` because its needs were simple single-line
   series. Recommendation: keep Chart.js under a thin Vue wrapper component rather than
   reimplementing annotations/min-max banding by hand. Not decided either way here.
3. **`root_url`/config plumbing** — covered above; it's the small API change this plan would need,
   so it's a genuine question of whether a backend touch is acceptable (issue #25 says backend
   "as-is", which the config endpoint slightly violates).
4. **Sidebar current values on the Sensors page too, or Overview only?** The sidebar is the natural
   home for the current values, but whether it stays visible (with its values + tap-to-expand
   breakdown) on the Sensors page as well, or the Sensors page is a plain full-width table with the
   sidebar reduced to nav, is open. Leaning: keep the sidebar current values only on the Overview;
   the Sensors page already shows every value at a glance so a duplicate summary column is redundant.

## Implementation (phased checklist)

Phase 1 — scaffold and API/config plumbing:

- [ ] Stand up a Vite + Vue 3 + TypeScript app in the chosen location, with vue-router, bootstrap +
      bootstrap-icons, vitest, and (if this repo) a Vite build that outputs into the Django static
      dir so `nginx.conf` keeps serving `/static/` unchanged.
- [ ] Add `/api/config/` (or equivalent) exposing `site`/`title`/`root_url`/`value_types`/
      `plot_types`/`location` (resolves open question 3).
- [ ] Type the API responses (`current`, `sensors`, `history`, `history/goodweather`, `timeline`)
      as TypeScript interfaces — the current JSON is the contract; don't re-derive field names by
      reading `api/views.py` twice.
- [ ] SPA routing decision: vue-router history mode (needs Django/nginx to fall back to
      `index.html` on unknown routes) vs hash mode (no server change). Flag nginx fallback in the
      deploy docs if history mode.

Phase 2 — main view:

- [ ] Sidebar filled with the current values: one entry per `config.value_types` (label + value +
      unit + good/bad color), plus the overall GOOD/BAD banner and read time, polled from
      `/api/current/` (~10s).
- [ ] Tap-to-expand sensor breakdown over each current value: per-station breakdown for that
      sensor type from `/api/sensors/` (value, good/bad, `since`, delay comment), accordion-style
      (no hover) — a shortcut, not a replacement for the Sensors page.
- [ ] Sensors page: own route + sidebar nav entry with the full live table of every active sensor
      (station, sensor, value+unit, good, since, delay comment) from `/api/sensors/`, using
      `table-responsive` + `text-nowrap` for mobile.
- [ ] Day/night timeline, reworked as Vue component(s) instead of the raw-canvas `draw_timeline`.
- [ ] Good-weather history chart (solar elevation + good/bad bands) from
      `/api/history/goodweather/`.
- [ ] Per-type sensor history charts from `/api/history/<type>/`, preserving mean/min/max fanning
      and evaluator area annotations, on the chosen charting library.
- [ ] Mobile: off-canvas sidebar drawer (hamburger + backdrop, `280px` slide-in), tap-to-expand
      sensor breakdown, current values wrap, charts scale to viewport, `min-width: 0` +
      `table-responsive` for tabular content, no horizontal overflow at 390px — mirroring
      pyobs-web-admin's `base.html`.

Phase 3 — removal and cleanup:

- [ ] Drop `/docs/` (not migrated), and delete the old templates and vendored JS
      (`frontend/static/frontend/js/vendor/`, `app.js`, `app-sensors.js`, the Vue 2 `vue.min.js`)
      once the SPA is live-verified.
- [ ] Update `README.md` and the Docker/nginx notes for the new build step and static output.

## Tests

- Unit (vitest): the API type mapping and any pure helpers (time formatting, evaluator-area
  coloring, min/max dataset shaping).
- Component tests where cheap (current-value coloring, expand-in-place breakdown rendering).
- Playwright e2e against a running backend with `dummy`/`average` stations (there's a `dummy`
  station in `weather/stations/dummy.py`), asserting both views (Overview, Sensors) render and the
  polls return live data without console errors.
- Manual mobile-viewport pass (390px): sidebar drawer opens/closes, sensor breakdown expands on
  tap, Sensors table scrolls internally, no horizontal overflow — matching the sibling clients'
  convention.

## Consequences

- **Good:** one frontend stack across the pyobs web projects — same look, same build/test tooling,
  easier for anyone who knows pyobs-web-client to work on this.
- **Good:** the current vendored-JS-no-build setup has no way to catch JS breakage before deploy; a
  Vite + vitest + playwright setup fixes that.
- **Neutral:** a build step is introduced where there was none (Docker image or static volume now
  needs the Vite output). The current setup ships source JS directly.
- **Risk:** the SPA drops the server-rendered context if the config endpoint (or its client-side
  replacement) is skipped — the "Current" column and which plots render both depend on
  `value_types`/`plot_types`. Resolving open question 3 is a prerequisite, not optional.
- **Out of scope:** backend/API behavior changes beyond the minimal config endpoint, and the
  station/evaluator logic.
