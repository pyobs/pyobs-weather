# CLAUDE.md

Entry points for working in this repo.

## What this is

`pyobs-weather` aggregates data from several weather stations. Rules can be defined for when
weather is considered "good"; provides both a web frontend (Vue, in `frontend-vue/`) and an API.
Django + Celery + InfluxDB. Full installation, configuration, architecture, and REST API reference
live in [`docs/source/`](docs/source/) (Sphinx —
`cd docs && uv run --with sphinx --with sphinx-rtd-theme make html`).

## Design history and planning

This repo keeps its own local design docs, plans, and ADRs: `specs/plans/` (checklist-style;
folds into `design/` once shipped), `specs/design/` (living, one per feature), and `specs/adrs/`
(MADR-lite decision records) — see `specs/index.md` for the current lists. `pyobs-core`'s
`specs/` is the reference for the full fleet-wide convention (it additionally has `steering/`)
and holds any cross-repo docs that happen to touch this repo, tagged with a `Repos:` line.

## Tooling

- Backend: Django, managed via `uv` (`uv sync --group dev`)
- Format: `black` (config in `pyproject.toml`)
- No ruff/pyrefly config in this repo yet
- Frontend: Vue/Vite in `frontend-vue/` (`npm install`, `npm run dev`, `npm run build`)
