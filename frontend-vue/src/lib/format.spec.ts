import { describe, it, expect } from 'vitest'
import { formatValue, goodClass, timeUtc, datetimeUtc, delayComment, limitText, limitClass } from './format'
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
    limits: [],
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

describe('limitText', () => {
  it('formats a lower-bound danger band', () => {
    expect(limitText({ type: 'danger', min: 85 }, 'hPa')).toBe('bad ≥ 85 hPa')
  })
  it('formats an upper-bound band', () => {
    expect(limitText({ type: 'danger', max: 85 }, 'hPa')).toBe('bad ≤ 85 hPa')
  })
  it('formats a two-sided warning band', () => {
    expect(limitText({ type: 'warning', min: 80, max: 85 }, '°C')).toBe('warn 80–85 °C')
  })
  it('omits the unit when empty', () => {
    expect(limitText({ type: 'danger', min: 1 }, '')).toBe('bad ≥ 1')
  })
  it('trims trailing zeros', () => {
    expect(limitText({ type: 'danger', min: 80.0 }, '°C')).toBe('bad ≥ 80 °C')
  })
  it('returns empty for an empty band', () => {
    expect(limitText({ type: 'warning' }, '°C')).toBe('')
  })
})

describe('limitClass', () => {
  it('maps danger/warning to distinct classes', () => {
    expect(limitClass({ type: 'danger' })).toBe('text-danger')
    expect(limitClass({ type: 'warning' })).toBe('text-warning-emphasis')
  })
})
