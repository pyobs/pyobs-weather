# pyobs-weather frontend (Vue 3 + TypeScript + Vite)

Vue 3 + Vite + TypeScript + Bootstrap 5 single-page app for pyobs-weather, consuming the Django
backend's JSON API under `/api/`. Replaces the old server-rendered Django + jQuery + Chart.js
frontend (see `../specs/plans/2026-08-18-modernize-frontend.md`).

## Development

```sh
npm install
npm run dev
```

The Vite dev server proxies `/api`, `/admin`, and `/static` to `http://localhost:8000`, so run the
Django dev server alongside (`uv run ./manage.py runserver` from the repo root).

## Build

```sh
npm run build
```

Outputs to `../pyobs_weather/frontend/static/frontend/dist/`, which Django's `collectstatic` picks
up automatically. Asset URLs are built with a placeholder base (`/__PYOBS_STATIC_BASE__/frontend/dist/`),
since `ROOT_URL` is only known at container runtime; `pyobs_weather/frontend/views.py` rewrites it
to the real `STATIC_URL` when it serves `index.html`.

## Tests

```sh
npm run test:unit
npm run test:e2e
npm run type-check
```

The e2e suite (Playwright) runs against the Vite dev server with `/api/` requests mocked, so no
backend is needed. Install browsers first with `npx playwright install chromium`.

