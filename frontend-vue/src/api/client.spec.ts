import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { apiUrl, getCsrfToken, historyExportUrl, loginUrl, logoutUrl, setRootUrl } from './client'

describe('api client', () => {
  beforeEach(() => {
    setRootUrl('/')
  })

  it('defaults the root URL to /', () => {
    expect(apiUrl('current/')).toBe('/api/current/')
  })

  it('prefixes with a configured root URL', () => {
    setRootUrl('/weather/')
    expect(apiUrl('current/')).toBe('/weather/api/current/')
  })

  it('normalizes a missing trailing slash', () => {
    setRootUrl('/weather')
    expect(apiUrl('sensors/')).toBe('/weather/api/sensors/')
  })
})

describe('keycloak login/logout URLs', () => {
  beforeEach(() => {
    setRootUrl('/')
  })

  it('builds the login URL under the root URL', () => {
    setRootUrl('/weather/')
    expect(loginUrl()).toBe('/weather/accounts/keycloak/login/')
  })

  it('builds the logout URL under the root URL', () => {
    setRootUrl('/weather/')
    expect(logoutUrl()).toBe('/weather/accounts/keycloak/logout/')
  })
})

describe('historyExportUrl', () => {
  beforeEach(() => {
    setRootUrl('/')
  })

  it('builds the export URL with start/end query params', () => {
    expect(historyExportUrl('thiesws', '2026-01-01', '2026-01-31')).toBe(
      '/api/history/export/thiesws/?start=2026-01-01&end=2026-01-31',
    )
  })

  it('URL-encodes the station code', () => {
    expect(historyExportUrl('a/b', '2026-01-01', '2026-01-31')).toBe(
      '/api/history/export/a%2Fb/?start=2026-01-01&end=2026-01-31',
    )
  })
})

describe('getCsrfToken', () => {
  afterEach(() => {
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT'
  })

  it('returns null when no csrftoken cookie is set', () => {
    expect(getCsrfToken()).toBeNull()
  })

  it('reads the csrftoken cookie value', () => {
    document.cookie = 'csrftoken=abc123'
    expect(getCsrfToken()).toBe('abc123')
  })
})
