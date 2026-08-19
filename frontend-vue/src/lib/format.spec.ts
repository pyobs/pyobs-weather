import { describe, it, expect } from 'vitest'
import { formatValue, goodClass, timeUtc, datetimeUtc, delayComment } from './format'
import type { SensorRow } from '../api/types'

describe('formatValue', () => {
  it('returns N/A for null', () => {
    expect(formatValue(null)).toBe('N/A')
  })
  it('formats numbers to one decimal place', () => {
    expect(formatValue(3.14159)).toBe('3.1')
  })
})

describe('goodClass', () => {
  it('maps true/false/null to distinct classes', () => {
    expect(goodClass(true)).toBe('sensor-good')
    expect(goodClass(false)).toBe('sensor-bad')
    expect(goodClass(null)).toBe('sensor-unknown')
  })
})

describe('time formatting', () => {
  it('formats UTC time-of-day', () => {
    expect(timeUtc('2020-01-01T12:34:56Z')).toBe('12:34:56')
  })
  it('returns N/A for a null time', () => {
    expect(timeUtc(null)).toBe('N/A')
  })
  it('formats full UTC datetime', () => {
    expect(datetimeUtc('2020-01-01T12:34:56Z')).toBe('2020-01-01 12:34:56')
  })
})

describe('delayComment', () => {
  const base: SensorRow = {
    station_code: 'a',
    station_name: 'A',
    type_code: 'temp',
    type_name: 'Temp',
    unit: 'C',
    value: 1,
    good: null,
    since: null,
    good_since: null,
    bad_since: null,
    delay_good: 0,
    delay_bad: 0,
  }

  it('returns empty when no delay is pending', () => {
    expect(delayComment(base)).toBe('')
  })
  it('reports a pending good delay', () => {
    const row: SensorRow = { ...base, good_since: new Date(Date.now() - 1000).toISOString(), delay_good: 100000 }
    expect(delayComment(row)).toMatch(/^good delayed for \d+s$/)
  })
  it('reports a pending bad delay', () => {
    const row: SensorRow = { ...base, bad_since: new Date(Date.now() - 1000).toISOString(), delay_bad: 100000 }
    expect(delayComment(row)).toMatch(/^bad delayed for \d+s$/)
  })
})
