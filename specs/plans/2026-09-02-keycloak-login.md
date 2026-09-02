# Plan: Keycloak login for pyobs-weather

Issues: #33 (prerequisite for #6). Repo: pyobs-weather only — pyobs-auth 2.1.0 already has
everything needed (`REQUIRED_GROUPS`, `KeycloakSessionRefreshMiddleware`), no upstream changes
required.

Status: sections 1-5 implemented and committed to `develop` 2026-09-02 (`21ba43b`). Section 0
(Keycloak admin-console config, per site) is still open and blocks actually enabling login
anywhere — the code is safe to have merged ahead of it (`KEYCLOAK_SERVER_URL` unset is a no-op,
same as archive/portal's rollout).

Unlike pyobs-archive/pyobs-portal's cutovers (pyobs-core #823), this is greenfield: weather has
zero auth code today (no login, no `is_staff` checks anywhere), so it builds straight against
pyobs-auth 2.1.0 rather than retrofitting an activation-gate migration.

## 0. Keycloak admin config (not pyobs code, one pass per deployment)

Weather is deployed per-site, not as a fleet-wide singleton (unlike archive) — so this section
runs once per installation, each with its own client and group, following the same
per-installation convention `pyobs-monet`/`pyobs-iagvt`/`pyobs-iag50` already use for
web-admin/portal (a single `/pyobs-weather` group would authorize a user for every site's weather
page at once). Confirmed for IAG50cm in `pyobs-iag50`'s `specs/design/keycloak-service-topology.md`:
client `iag50srv-weather`, group `/pyobs-weather-iag50srv`. Other sites (monet south/north, iagvt)
follow the same `<site>-weather` / `/pyobs-weather-<site>` pattern once each is scoped.

- [ ] Per site: run `central/auth/create_client.sh <site>-weather <redirect-uri>
      <post-logout-redirect-uri> /pyobs-weather-<site>` (creates the client, wires the `groups`
      default scope, and creates the empty group in one step)
- [ ] Per site: populate the created group with authorized users — **fail-closed**: until this is
      populated, every login at that site is refused
- [ ] Per site: verify the shared realm's "Group Membership" protocol mapper (added during #823)
      already covers the new client — don't recreate it

## 1. pyobs-auth dependency

- [x] Add `pyobs-auth>=2.1.0` to `pyproject.toml`
- [x] `INSTALLED_APPS`: add `pyobs_auth`
- [x] `MIDDLEWARE`: add `pyobs_auth.middleware.KeycloakSessionRefreshMiddleware` after
      `AuthenticationMiddleware`
- [x] `AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]` (Keycloak login is
      view-based, not a backend)
- [x] Include `pyobs_auth.urls` in `pyobs_weather/urls.py` under `accounts/keycloak/` — routed
      before the SPA fallback; `frontend/urls.py`'s negative-lookahead regex now also excludes
      `accounts/`/`accounts$`.

## 2. User resolution

- [x] New `pyobs_weather.authentication` app: `KeycloakIdentity` model (`OneToOneField` to `User` +
      unique `keycloak_sub`), migration `0001_initial`
- [x] `resolve_user(claims)`: match by `sub`, else by email, else by username, else mint new
      `User(is_active=True)`
- [x] No `is_staff`/`is_superuser` sync — Django admin stays local-only (`createsuperuser`)

## 3. Settings

- [x] `PYOBS_AUTH` dict: `SERVER_URL`/`REALM`/`CLIENT_ID`/`CLIENT_SECRET`/`REDIRECT_URI`/
      `POST_LOGOUT_REDIRECT_URI`/`IDP_HINT`/`IDP_LABEL` from `KEYCLOAK_*` env vars,
      `USER_RESOLVER`, `REQUIRED_GROUPS` from `KEYCLOAK_REQUIRED_GROUP` (falls back to
      `/pyobs-weather` if unset, but that fallback is a placeholder, not a real group anywhere —
      per-installation per section 0, so every real deployment's `local_settings.py` must override
      it with that site's actual group, e.g. `/pyobs-weather-iag50srv`)
- [x] `SESSION_ENGINE`: confirmed no change needed — weather never overrides it, so Django's
      db-backed default already applies
- [x] Documented new env vars in `.env.example` and `docs/source/configuration.rst`

## 4. SPA-facing auth surface

- [x] `GET /api/me/` → `{authenticated: bool, username: str|null}`; `/api/config/` also gained
      `keycloak_enabled` so the frontend can hide the login link when Keycloak isn't configured
- [x] `frontend-vue`: plain `<a :href="loginUrl()">` in `App.vue`'s sidebar (real page nav);
      logout builds and submits a hidden `<form method=post>` to `pyobs_auth:logout` (a real
      navigation, not `fetch()`, so Keycloak's RP-Initiated-Logout redirect actually loads in the
      browser) — `useAuth.ts` composable, CSRF token read from the cookie set by
      `frontend/views.py`'s now-`@ensure_csrf_cookie`-decorated `index` view

## 5. Tests

- [x] `resolve_user`: 7 tests (new user minted active, no staff/superuser flags, matched by
      `sub`/email/username, username fallback) — `pyobs_weather/authentication/tests.py`
- [ ] `REQUIRED_GROUPS` gate itself: not re-tested here — that logic lives in and is already
      covered by pyobs-auth's own `authorize()` test suite; weather only sets the setting
- [x] `manage.py check` clean with `KEYCLOAK_SERVER_URL` set (validates the routing-order fix);
      `manage.py test` — all new tests pass (2 `/api/me/` tests added too); frontend
      `vue-tsc -b` and `vitest run` (7 new client tests) both clean; production `npm run build`
      succeeds; Sphinx docs build clean, no new warnings

## 6. Not in this plan

- Actually gating the previous-nights/historic-data endpoint — that's #6's job; this just gives it
  `request.user.is_authenticated` to check
- Any weather-admin privilege tier — ruled out (binary gate only)
- Stale-tab handling if a group is revoked mid-session — next API call just 403s, no proactive SPA
  push
