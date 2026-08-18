<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import Chart from '../lib/chart'
import { fetchJson } from '../api/client'
import { usePolling } from '../composables/usePolling'
import type { GoodWeatherResponse } from '../api/types'

const canvasRef = ref<HTMLCanvasElement | null>(null)
const { data } = usePolling<GoodWeatherResponse>(() => fetchJson('history/goodweather/'), 60000)

let chart: Chart | null = null

function render(resp: GoodWeatherResponse | null) {
  if (!canvasRef.value || !resp) return

  const sun = resp.sun.time.map((t, i) => ({ x: new Date(t).getTime(), y: resp.sun.alt[i] }))

  const annotations: Record<string, unknown>[] = []
  const changes = resp.changes
  changes.forEach((change, i) => {
    if (i === 0) {
      annotations.push({
        type: 'box',
        display: true,
        xScaleID: 'x',
        yScaleID: 'y',
        drawTime: 'beforeDatasetsDraw',
        borderWidth: 0,
        xMax: new Date(change.time).getTime(),
        backgroundColor: change.good ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 255, 0, 0.5)',
      })
    }
    const ann: Record<string, unknown> = {
      type: 'box',
      display: true,
      xScaleID: 'x',
      yScaleID: 'y',
      drawTime: 'beforeDatasetsDraw',
      borderWidth: 0,
      xMin: new Date(change.time).getTime(),
      backgroundColor: change.good ? 'rgba(0, 255, 0, 0.5)' : 'rgba(255, 0, 0, 0.5)',
    }
    if (i + 1 < changes.length) ann.xMax = new Date(changes[i + 1].time).getTime()
    annotations.push(ann)
  })
  annotations.push({
    type: 'line',
    scaleID: 'y',
    value: 0,
    borderColor: 'rgba(0, 0, 0, 0.5)',
    borderWidth: 1,
  })

  const now = Date.now()
  const datasets = [
    {
      label: '',
      data: sun,
      backgroundColor: 'rgba(255, 255, 100, 0.5)',
      borderColor: 'rgba(255, 255, 100, 1)',
      pointRadius: 0,
      fill: false,
      tension: 0.2,
    },
  ]

  if (!chart) {
    chart = new Chart(canvasRef.value, {
      type: 'line',
      data: { datasets },
      options: {
        animation: false,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          annotation: { annotations },
        },
        scales: {
          x: {
            type: 'time',
            min: now - 24 * 3600 * 1000,
            max: now,
            title: { display: true, text: 'Time [UT]' },
          },
          y: { title: { display: true, text: 'Sun/good' } },
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
