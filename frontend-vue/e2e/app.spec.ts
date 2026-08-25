import { test, expect, type Page } from '@playwright/test'

const CONFIG = {
  site: 'MONET/N @ McDonald Observatory',
  title: 'Weather at MONET/N @ McDonald Observatory',
  root_url: '/',
  value_types: [
    { code: 'temp', name: 'Temperature', unit: '°C' },
    { code: 'humid', name: 'Humidity', unit: '%' },
  ],
  plot_types: [{ code: 'temp', name: 'Temperature', unit: '°C' }],
  location: { longitude: '104°01\'18" W', latitude: '30°40\'18" N', elevation: 2075.0 },
}

const CURRENT = {
  time: '2026-08-18T12:00:00Z',
  good: true,
  sensors: {
    temp: { good: true, value: 12.5 },
    humid: { good: false, value: 80.0 },
  },
}

const SENSORS = [
  {
    station_code: 'average',
    station_name: 'Average',
    type_code: 'temp',
    type_name: 'Temperature',
    unit: '°C',
    value: 12.5,
    good: true,
    since: '2026-08-18T11:00:00Z',
    good_since: null,
    bad_since: null,
    delay_good: 0,
    delay_bad: 0,
    limits: [
      { type: 'danger', min: 30 },
      { type: 'warning', min: 20, max: 30 },
    ],
  },
  {
    station_code: 'monet',
    station_name: 'MONET',
    type_code: 'temp',
    type_name: 'Temperature',
    unit: '°C',
    value: 13.0,
    good: true,
    since: null,
    good_since: null,
    bad_since: null,
    delay_good: 0,
    delay_bad: 0,
    limits: [],
  },
]

const TIMELINE = {
  time: '2026-08-18T12:00:00Z',
  events: [
    '2026-08-18T01:00:00Z',
    '2026-08-18T02:00:00Z',
    '2026-08-18T03:00:00Z',
    '2026-08-18T04:00:00Z',
  ],
}

const GOOD_WEATHER = {
  changes: [{ time: '2026-08-17T12:00:00Z', good: true }],
  sun: { time: ['2026-08-17T12:00:00Z', '2026-08-18T12:00:00Z'], alt: [0.0, 30.0] },
}

const HISTORY = {
  stations: [
    {
      code: 'monet',
      name: 'MONET',
      color: '#ff0000',
      data: [{ time: '2026-08-18T10:00:00Z', value: 12.0, min: 11.0, max: 13.0 }],
    },
  ],
  areas: [{ type: 'danger', min: 0.0, max: 1.0 }],
}

async function mockApi(page: Page) {
  await page.route(
    (url) => new URL(url).pathname.startsWith('/api/'),
    (route) => {
      const path = new URL(route.request().url()).pathname
      let body: unknown
      if (path.endsWith('/config/')) body = CONFIG
      else if (path.endsWith('/current/')) body = CURRENT
      else if (path.endsWith('/sensors/')) body = SENSORS
      else if (path.endsWith('/timeline/')) body = TIMELINE
      else if (path.includes('/history/goodweather/')) body = GOOD_WEATHER
      else if (path.includes('/history/')) body = HISTORY
      else {
        route.fulfill({ status: 404, body: '{}' })
        return
      }
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
    },
  )
}

test.beforeEach(async ({ page }) => {
  await mockApi(page)
})

test('overview renders current values and plots', async ({ page }, testInfo) => {
  await page.goto('/')
  if (testInfo.project.name === 'mobile') {
    await page.getByRole('button', { name: 'Open sidebar' }).click()
  }
  await expect(page.getByText('Temperature').first()).toBeVisible()
  await expect(page.getByText('12.5')).toBeVisible()
  await expect(page.getByText('GOOD')).toBeVisible()
})

test('sensors page shows the live table', async ({ page }) => {
  await page.goto('/sensors')
  await expect(page.getByText('Sensor status')).toBeVisible()
  await expect(page.getByRole('cell', { name: 'MONET' })).toBeVisible()
  await expect(page.getByText('13.0')).toBeVisible()
  await expect(page.getByText('bad ≥ 30 °C')).toBeVisible()
  await expect(page.getByText('warn 20–30 °C')).toBeVisible()
})

test('no horizontal overflow on mobile', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile', 'mobile-only')
  await page.goto('/')
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  )
  expect(overflow).toBe(false)
})
