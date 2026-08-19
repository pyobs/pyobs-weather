const ICONS: Record<string, string> = {
  temp: 'bi-thermometer-half',
  humid: 'bi-droplet-half',
  press: 'bi-speedometer2',
  windspeed: 'bi-wind',
  winddir: 'bi-compass',
  rain: 'bi-cloud-rain',
  skytemp: 'bi-cloud-haze2',
  sunalt: 'bi-sun',
}

export function sensorIcon(code: string): string {
  return ICONS[code] ?? 'bi-question-circle'
}
