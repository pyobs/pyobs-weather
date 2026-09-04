# User-defined plot colors adapt to theme client-side; `Station.color` stays a single free-form value

status: accepted
date: 2026-09-03

## Context and Problem Statement

`Station.color` (`pyobs_weather/weather/models.py`) is a single admin-editable string ("Plot
color", max 20 chars, default `rgba(0, 0, 0, 0.1)`) used to draw that station's line/band in
`SensorPlot.vue`. Since the frontend gained light/dark themes, one stored color can no longer be
legible on both: a dark color (including the black default) is invisible on the dark surface
(`--pyobs-surface-bg: #1a1d21`), a bright one washes out on the light surface (`#ffffff`).

Two more defects compound this, found while scoping the fix (pyobs-core#863):

- `withAlpha()` (`frontend-vue/src/lib/color.ts`) only rewrites `#rgb`/`#rrggbb` hex strings; a
  stored `rgba(...)` value (the field's own default) passes through unchanged, so `SensorPlot.vue`'s
  `withAlpha(color, 0.5)` / `withAlpha(color, 0.1)` overrides are silently no-ops for it.
  `GoodWeatherChart.vue`'s zero line is hardcoded `rgba(0, 0, 0, 0.5)`, invisible on dark.
- Chart chrome (grid, ticks, axis text) isn't set at all — charts run on Chart.js's light-themed
  defaults (`#666` ticks, `rgba(0,0,0,0.1)` grid), unreadable on dark, and are never recreated when
  the user toggles the theme (`App.vue` holds `theme`, `SensorPlot.vue`/`GoodWeatherChart.vue`
  don't watch it).

pyobs-core#863 originally scoped this alongside pyobs-portal (Plotly, hardcoded-dark constants)
and pyobs-web-client (canvas, hardcoded-dark colors). Restricted here to pyobs-weather only: the
other two are separate codebases with their own chart libraries and no shared component to land a
fix in, so a single cross-repo ADR would just be three unrelated decisions wearing one number.
They can get their own issue/ADR in their own repo if and when someone picks them up.

## Considered Options

* **Per-theme color fields** — add `Station.color_light` / `Station.color_dark`, let the admin
  pick both. Correct by construction, but doubles the admin UI, needs a migration for every
  existing station, and does nothing about the `withAlpha()` bug or chart chrome — those still
  need a code fix regardless of how many colors are stored.
* **Curated palette** — replace the free-form hex field with a fixed set of theme-safe colors,
  station picks by name. Guarantees contrast but removes the flexibility the field currently
  offers (arbitrary admin-chosen hex) and still requires migrating existing station values into
  the new palette.
* **Automatic client-side adaptation** (chosen) — keep `Station.color` as one free-form value;
  in `lib/color.ts`, convert it to HSL, keep hue and saturation, and clamp lightness against the
  active theme's surface color until the pair clears a minimum contrast ratio (WCAG 1.4.11,
  ≥3:1 for graphical/UI elements — plot lines and bands are non-text). Same function fixes
  `withAlpha()`'s `rgba(...)` blind spot in the process, since both need to parse arbitrary CSS
  color strings anyway.

## Decision Outcome

Chosen option: automatic client-side adaptation, no change to `Station.color` or the admin UI.

The two rejected options both solve only the "one stored value, two surfaces" half of the
problem and leave `withAlpha()` and the unstyled chart chrome untouched — those need fixing
either way, and once `lib/color.ts` can correctly parse and adjust any CSS color string, adapting
lightness per-theme is the same piece of work, not an additional one. Keeping a single stored
value also means no Django migration, no admin UI change, and no one-time backfill for existing
stations (several of which use the black-ish default and would need re-picking under either
rejected option regardless).

### Consequences

* Good, because existing `Station.color` values keep working without a migration or admin
  re-entry — including ones already set to `rgba(...)`, once `withAlpha()` is fixed to handle
  them.
* Good, because the same color-parsing work fixes `withAlpha()`'s `rgba(...)` blind spot and the
  zero-contrast default (`rgba(0, 0, 0, 0.1)`) as a side effect, rather than as separate work.
* Good, because chart chrome tokens (grid/ticks/axis text/zero line/bands) can live next to the
  adaptation function and read `--pyobs-surface-*` via `getComputedStyle`, giving one place that
  needs to react when `SensorPlot.vue`/`GoodWeatherChart.vue` start watching the theme ref instead
  of only computing colors on mount.
* Neutral, because the admin still can't preview how a chosen color will render in either theme
  before saving — an admin picking a mid-gray sees no immediate contrast warning. Not addressed
  here; would need a Django admin widget change, out of scope for a client-side fix.
* Bad, because clamping lightness for contrast means the rendered color is never exactly the hex
  the admin entered in either theme (by design — the literal value fails contrast on at least one
  surface) — acceptable since the goal is a recognizable, same-hue color that stays readable, not
  a pixel-exact swatch.
