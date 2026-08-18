import type { SensorRow } from '../api/types'

export function formatValue(value: number | null): string {
  if (value === null) return 'N/A'
  return value.toFixed(1)
}

export function goodClass(good: boolean | null): string {
  if (good === true) return 'sensor-good'
  if (good === false) return 'sensor-bad'
  return 'sensor-unknown'
}

function pad(n: number): string {
  return String(n).padStart(2, '0')
}

export function timeUtc(iso: string | null): string {
  if (!iso) return 'N/A'
  const d = new Date(iso)
  return `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}`
}

export function datetimeUtc(iso: string | null): string {
  if (!iso) return 'N/A'
  const d = new Date(iso)
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())} ${timeUtc(iso)}`
}

export function delayComment(row: SensorRow): string {
  const now = Date.now()
  if (row.good_since) {
    const elapsed = (now - new Date(row.good_since).getTime()) / 1000
    return `good delayed for ${Math.max(0, row.delay_good - elapsed).toFixed(0)}s`
  }
  if (row.bad_since) {
    const elapsed = (now - new Date(row.bad_since).getTime()) / 1000
    return `bad delayed for ${Math.max(0, row.delay_bad - elapsed).toFixed(0)}s`
  }
  return ''
}
