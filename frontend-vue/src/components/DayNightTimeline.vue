<script setup lang="ts">
import { computed } from 'vue'
import { fetchJson } from '../api/client'
import { usePolling } from '../composables/usePolling'
import type { TimelineResponse } from '../api/types'

const { data } = usePolling<TimelineResponse>(() => fetchJson('timeline/'), 60000)

const pct = computed(() => {
  const events = data.value?.events ?? []
  if (events.length < 4) return null
  const [sunset, sunsetTwilight, sunriseTwilight, sunrise] = events.map((e) => new Date(e).getTime())
  const total = sunrise - sunset
  if (total <= 0) return null
  const now = data.value?.time ? new Date(data.value.time).getTime() : Date.now()
  const clamp = (v: number) => Math.min(100, Math.max(0, v))
  return {
    sunsetTwilight: clamp(((sunsetTwilight - sunset) / total) * 100),
    sunriseTwilight: clamp(((sunriseTwilight - sunset) / total) * 100),
    now: clamp(((now - sunset) / total) * 100),
  }
})

const gradient = computed(() => {
  const p = pct.value
  if (!p) return 'transparent'
  return `linear-gradient(to right, yellow 0%, black ${p.sunsetTwilight}%, black ${p.sunriseTwilight}%, yellow 100%)`
})

function fmt(iso: string | undefined): string {
  if (!iso) return '--:--'
  return new Date(iso).toISOString().slice(11, 16)
}

const events = computed(() => data.value?.events ?? [])
</script>

<template>
  <div v-if="data">
    <div class="timeline-bar" :style="{ background: gradient }">
      <div
        v-if="pct"
        class="timeline-marker bg-white"
        :style="{ left: pct.sunsetTwilight + '%' }"
      ></div>
      <div
        v-if="pct"
        class="timeline-marker bg-white"
        :style="{ left: pct.sunriseTwilight + '%' }"
      ></div>
      <div v-if="pct" class="timeline-marker bg-danger" :style="{ left: pct.now + '%' }"></div>
    </div>
    <div class="d-flex justify-content-between small text-muted mt-1">
      <span>Sunset {{ fmt(events[0]) }} UT</span>
      <span>Dawn {{ fmt(events[2]) }} UT</span>
    </div>
    <div class="d-flex justify-content-between small text-muted">
      <span>Dusk {{ fmt(events[1]) }} UT</span>
      <span>Sunrise {{ fmt(events[3]) }} UT</span>
    </div>
  </div>
</template>
