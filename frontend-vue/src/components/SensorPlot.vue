<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import Chart from '../lib/chart'
import { fetchJson } from '../api/client'
import { usePolling } from '../composables/usePolling'
import { useTheme } from '../composables/useTheme'
import { adaptToSurface, cssVar, withAlpha } from '../lib/color'
import { chartChromeColors } from '../lib/chartTheme'
import type { HistoryResponse } from '../api/types'

const props = defineProps<{ typeCode: string; label: string; unit: string }>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const { data } = usePolling<HistoryResponse>(() => fetchJson(`history/${props.typeCode}/`), 60000)
const { theme } = useTheme()

let chart: Chart | null = null

function render(resp: HistoryResponse | null) {
  if (!canvasRef.value || !resp) return

  const surfaceBg = cssVar('--pyobs-surface-bg', '#ffffff')
  const chrome = chartChromeColors()

  const datasets = resp.stations
    // backend's history() view already excludes the average station from `stations`
    .flatMap((station) => {
      const ts = (iso: string) => new Date(iso).getTime()
      const mean = station.data.map((p) => ({ x: ts(p.time), y: p.value }))
      const min = station.data.map((p) => ({ x: ts(p.time), y: p.min }))
      const max = station.data.map((p) => ({ x: ts(p.time), y: p.max }))
      const color = adaptToSurface(station.color, surfaceBg)
      return [
        {
          label: '',
          data: min,
          borderWidth: 0,
          backgroundColor: 'transparent',
          pointRadius: 0,
          fill: false,
        },
        {
          label: '',
          data: max,
          borderWidth: 0,
          backgroundColor: withAlpha(color, 0.1),
          pointRadius: 0,
          fill: '-1',
        },
        {
          label: station.name,
          data: mean,
          borderColor: withAlpha(color, 0.5),
          backgroundColor: withAlpha(color, 0.1),
          borderWidth: 2,
          pointRadius: 0,
          fill: false,
          tension: 0.2,
        },
      ]
    })

  const annotations = resp.areas.map((area) => {
    const ann: Record<string, unknown> = {
      type: 'box',
      display: true,
      yScaleID: 'y',
      drawTime: 'beforeDatasetsDraw',
      backgroundColor: area.type === 'danger' ? 'rgba(255, 0, 0, 0.1)' : 'rgba(255, 255, 0, 0.1)',
    }
    if (area.min !== undefined) ann.yMin = area.min
    if (area.max !== undefined) ann.yMax = area.max
    return ann
  })

  if (!chart) {
    chart = new Chart(canvasRef.value, {
      type: 'line',
      data: { datasets },
      options: {
        animation: false,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: { filter: (item) => item.text !== '', color: chrome.text },
          },
          tooltip: chrome.tooltip,
          annotation: { annotations },
        },
        scales: {
          x: {
            type: 'time',
            title: { display: true, text: 'Time [UT]', color: chrome.muted },
            grid: { color: chrome.grid },
            ticks: { color: chrome.muted },
          },
          y: {
            title: { display: true, text: props.label, color: chrome.muted },
            grid: { color: chrome.grid },
            ticks: { color: chrome.muted },
          },
        },
      },
    })
  } else {
    chart.data.datasets = datasets
    chart.options.plugins!.annotation!.annotations = annotations
    chart.update()
  }
}

watch(data, (v) => render(v), { immediate: true })

// theme change alone doesn't touch `data`, and scale/plugin colors are baked in at chart
// creation — simplest correct fix is to recreate the chart rather than patch every option
watch(theme, () => {
  chart?.destroy()
  chart = null
  render(data.value)
})

onBeforeUnmount(() => {
  chart?.destroy()
  chart = null
})
</script>

<template>
  <div class="chart-wrapper">
    <canvas ref="canvasRef"></canvas>
  </div>
</template>
