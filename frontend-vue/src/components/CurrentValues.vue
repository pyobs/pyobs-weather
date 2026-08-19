<script setup lang="ts">
import { computed, ref } from 'vue'
import { fetchJson } from '../api/client'
import { usePolling } from '../composables/usePolling'
import { useConfig } from '../composables/useConfig'
import { formatValue, goodClass, timeUtc, delayComment } from '../lib/format'
import { sensorIcon } from '../lib/sensorIcon'
import type { CurrentResponse, SensorRow } from '../api/types'

const { config } = useConfig()

const { data: current } = usePolling<CurrentResponse>(() => fetchJson('current/'), 10000)
const { data: sensors } = usePolling<SensorRow[]>(() => fetchJson('sensors/'), 10000)

const expanded = ref<Set<string>>(new Set())

function toggle(code: string) {
  const next = new Set(expanded.value)
  if (next.has(code)) next.delete(code)
  else next.add(code)
  expanded.value = next
}

function breakdownFor(code: string): SensorRow[] {
  return (sensors.value ?? []).filter((s) => s.type_code === code)
}

const overallGood = computed(() => current.value?.good ?? null)
</script>

<template>
  <div>
    <div class="d-flex align-items-center justify-content-between px-2 py-1">
      <span class="fw-semibold" :class="goodClass(overallGood)">
        {{ overallGood === null ? 'Weather' : overallGood ? 'GOOD' : 'BAD' }}
      </span>
      <span class="text-muted" style="font-size: 0.7rem">{{ timeUtc(current?.time ?? null) }} UT</span>
    </div>

    <div v-for="type in config?.value_types ?? []" :key="type.code">
      <button class="current-value" @click="toggle(type.code)" :aria-expanded="expanded.has(type.code)">
        <span class="d-flex align-items-center gap-2">
          <i class="bi bi-chevron-right" :class="{ 'rotate-90': expanded.has(type.code) }" style="font-size: 0.7rem"></i>
          <i class="bi value-icon" :class="sensorIcon(type.code)"></i>
          <span class="me-auto">{{ type.name }}</span>
          <span class="d-flex flex-column align-items-end lh-1">
            <span class="fw-semibold" :class="goodClass(current?.sensors[type.code]?.good ?? null)">
              {{ formatValue(current?.sensors[type.code]?.value ?? null) }}
            </span>
            <span class="unit">{{ type.unit }}</span>
          </span>
        </span>
      </button>

      <div v-if="expanded.has(type.code)" class="px-2 pb-2">
        <div v-for="row in breakdownFor(type.code)" :key="row.station_code + row.type_code" class="breakdown-row py-1">
          <div class="d-flex gap-2">
            <span class="me-auto text-muted">{{ row.station_name }}</span>
            <span :class="goodClass(row.good)">{{ formatValue(row.value) }} {{ row.unit }}</span>
          </div>
          <div v-if="delayComment(row)" class="text-muted" style="font-size: 0.7rem">{{ delayComment(row) }}</div>
        </div>
        <div v-if="breakdownFor(type.code).length === 0" class="breakdown-row text-muted py-1">No stations</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rotate-90 {
  transform: rotate(90deg);
}
</style>
