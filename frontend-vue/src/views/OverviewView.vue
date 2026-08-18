<script setup lang="ts">
import { useConfig } from '../composables/useConfig'
import DayNightTimeline from '../components/DayNightTimeline.vue'
import GoodWeatherChart from '../components/GoodWeatherChart.vue'
import SensorPlot from '../components/SensorPlot.vue'

const { config } = useConfig()
</script>

<template>
  <div v-if="config">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-0">{{ config.site }}</h4>
        <div class="text-muted small">
          {{ config.location.longitude }}, {{ config.location.latitude }},
          {{ config.location.elevation.toFixed(0) }}m
        </div>
      </div>
    </div>

    <div class="mb-4">
      <DayNightTimeline />
    </div>

    <h5>Plots for last 24h</h5>
    <div class="mb-4">
      <GoodWeatherChart />
    </div>

    <div v-for="type in config.plot_types" :key="type.code" class="mb-4">
      <SensorPlot :type-code="type.code" :label="type.name" :unit="type.unit" />
    </div>
  </div>
  <div v-else class="text-muted">Loading…</div>
</template>
