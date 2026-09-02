# Plans

Implementation plans, checklist-style. A plan moves/folds into `design/` once it ships.

- [2026-08-18-modernize-frontend.md](2026-08-18-modernize-frontend.md) — replace the
  server-rendered Django + jQuery + Chart.js frontend with Vue 3 + Vite + TypeScript + Bootstrap 5,
  matching the other pyobs web projects, and rework the sensor plots. **implemented, closed**
  (#25, PR #26)
- [2026-09-02-keycloak-login.md](2026-09-02-keycloak-login.md) — add Keycloak SSO login via
  pyobs-auth 2.1.0, greenfield (no prior auth code), prerequisite for gating historic-data
  download. (#33, prerequisite for #6)
