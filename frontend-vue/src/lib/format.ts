import type { HistoryArea, SensorRow } from '../api/types'

export function formatValue(value: number | null): string {
  if (value === null) return 'N/A'
  if (value === 0 || value === 1) return String(value)
  return value.toFixed(1)
}

/** Trim a limit bound to a readable number, e.g. 85 -> "85", 80.5 -> "80.5". */
function trimNumber(value: number): string {
  return String(Number(value.toFixed(2)))
}

/** Render one evaluator limit band as text, e.g. "bad ≥ 85 °C" or "warn 80–85 °C". */
export function limitText(limit: HistoryArea, unit: string): string {
  let range: string
  if (limit.min !== undefined && limit.max !== undefined) {
    range = `${trimNumber(limit.min)}–${trimNumber(limit.max)}`
  } else if (limit.min !== undefined) {
    range = `≥ ${trimNumber(limit.min)}`
  } else if (limit.max !== undefined) {
    range = `≤ ${trimNumber(limit.max)}`
  } else {
    return ''
  }
  const label = limit.type === 'danger' ? 'bad' : 'warn'
  return `${label} ${range}${unit ? ` ${unit}` : ''}`
}

export function limitClass(limit: HistoryArea): string {
  return limit.type === 'danger' ? 'text-danger' : 'text-warning-emphasis'
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
