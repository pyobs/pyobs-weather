declare global {
  interface Window {
    // injected by pyobs_weather/frontend/views.py when it serves index.html
    __PYOBS_ROOT_URL__?: string
  }
}

function normalize(url: string): string {
  return url.endsWith('/') ? url : url + '/'
}

// Set synchronously from the server-injected root URL so the very first request (config/) is
// already sent to the right place, instead of guessing '/' and never recovering under a
// non-default ROOT_URL.
let rootUrl = normalize(typeof window !== 'undefined' ? (window.__PYOBS_ROOT_URL__ ?? '/') : '/')

export function getRootUrl(): string {
  return rootUrl
}

export function setRootUrl(url: string) {
  rootUrl = normalize(url)
}

export function apiUrl(path: string): string {
  return `${rootUrl}api/${path}`
}

// start/end are plain 'YYYY-MM-DD' values from <input type="date">, sent as-is - the backend
// parses them with dateutil, which accepts a bare date.
export function historyExportUrl(stationCode: string, start: string, end: string): string {
  const params = new URLSearchParams({ start, end })
  return apiUrl(`history/export/${encodeURIComponent(stationCode)}/?${params}`)
}

export async function fetchJson<T>(path: string): Promise<T> {
  const url = apiUrl(path)
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`GET ${url} -> ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

// pyobs_auth's views (login/callback/logout), mounted by Django outside the SPA's own routes -
// a real page navigation, not a vue-router route or a fetch() call, since the OIDC redirect and
// Keycloak's RP-Initiated Logout both need the browser itself to follow them.
export function loginUrl(): string {
  return `${rootUrl}accounts/keycloak/login/`
}

export function logoutUrl(): string {
  return `${rootUrl}accounts/keycloak/logout/`
}

// pyobs_weather/frontend/views.py's index view is decorated with @ensure_csrf_cookie, so every
// SPA page load sets this - read here rather than fetched separately, since Django's CSRF
// middleware validates a submitted token against the cookie, not a server-side session value.
export function getCsrfToken(): string | null {
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : null
}
