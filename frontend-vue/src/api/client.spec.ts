import { describe, it, expect, beforeEach } from 'vitest'
import { apiUrl, setRootUrl } from './client'

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
