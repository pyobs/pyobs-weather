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

export async function fetchJson<T>(path: string): Promise<T> {
  const url = apiUrl(path)
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`GET ${url} -> ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}
