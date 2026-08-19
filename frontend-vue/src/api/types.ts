export interface SensorTypeInfo {
  code: string
  name: string
  unit: string
}

export interface ConfigResponse {
  site: string
  title: string
  root_url: string
  version: string
  value_types: SensorTypeInfo[]
  plot_types: SensorTypeInfo[]
  location: {
    longitude: string
    latitude: string
    elevation: number
  }
}

export interface CurrentResponse {
  time: string | null
  good: boolean
  sensors: Record<string, { good: boolean | null; value: number | null }>
}

export interface SensorRow {
  station_code: string
  station_name: string
  type_code: string
  type_name: string
  unit: string
  value: number | null
  good: boolean | null
  since: string | null
  good_since: string | null
  bad_since: string | null
  delay_good: number
  delay_bad: number
}

export interface HistoryPoint {
  time: string
  value: number | null
  min: number | null
  max: number | null
}

export interface HistoryStation {
  code: string
  name: string
  color: string
  data: HistoryPoint[]
}

export interface HistoryArea {
  type: 'danger' | 'warning'
  min?: number
  max?: number
}

export interface HistoryResponse {
  stations: HistoryStation[]
  areas: HistoryArea[]
}

export interface TimelineResponse {
  time: string
  events: string[]
}

export interface GoodWeatherResponse {
  changes: { time: string; good: boolean }[]
  sun: { time: string[]; alt: number[] }
}
