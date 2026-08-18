let rootUrl = '/'

export function setRootUrl(url: string) {
  rootUrl = url.endsWith('/') ? url : url + '/'
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
