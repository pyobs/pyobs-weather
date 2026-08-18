<script setup lang="ts">
import { fetchJson } from '../api/client'
import { usePolling } from '../composables/usePolling'
import { formatValue, goodClass, datetimeUtc, delayComment } from '../lib/format'
import type { SensorRow } from '../api/types'

const { data: sensors } = usePolling<SensorRow[]>(() => fetchJson('sensors/'), 10000)
</script>

<template>
  <div>
    <h4 class="mb-3">Sensor status</h4>
    <div class="table-responsive">
      <table class="table table-striped table-hover align-middle">
        <thead>
          <tr>
            <th>Station</th>
            <th>Sensor</th>
            <th>Value</th>
            <th>Good</th>
            <th>Since</th>
            <th>Comment</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sensor in sensors ?? []" :key="sensor.station_code + sensor.type_code" :class="goodClass(sensor.good)">
            <td>{{ sensor.station_name }}</td>
            <td>{{ sensor.type_name }}</td>
            <td class="text-nowrap">
              <strong>{{ formatValue(sensor.value) }}</strong>
              <small v-if="sensor.value !== null">{{ sensor.unit }}</small>
            </td>
            <td>{{ sensor.good === null ? '–' : sensor.good ? 'yes' : 'no' }}</td>
            <td class="text-nowrap">{{ datetimeUtc(sensor.since) }}</td>
            <td class="text-nowrap">{{ delayComment(sensor) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
