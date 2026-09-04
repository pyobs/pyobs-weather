<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchJson, historyExportUrl, loginUrl } from '../api/client'
import { useAuth } from '../composables/useAuth'
import { useConfig } from '../composables/useConfig'
import type { StationInfo } from '../api/types'

const { me } = useAuth()
const { config } = useConfig()

const stations = ref<StationInfo[]>([])
const stationsError = ref<Error | null>(null)
const selectedStation = ref('')
const start = ref('')
const end = ref('')
const downloadError = ref<string | null>(null)
const downloading = ref(false)

function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10)
}

onMounted(async () => {
  const now = new Date()
  end.value = isoDate(now)
  start.value = isoDate(new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000))

  try {
    // public endpoint, safe to fetch regardless of auth state; the download itself is what's
    // actually gated
    const all = await fetchJson<StationInfo[]>('stations/')
    stations.value = all.filter((s) => s.history).sort((a, b) => a.name.localeCompare(b.name))
    if (stations.value.length > 0) selectedStation.value = stations.value[0].code
  } catch (e) {
    stationsError.value = e as Error
  }
})

async function download() {
  downloadError.value = null
  downloading.value = true
  try {
    const res = await fetch(historyExportUrl(selectedStation.value, start.value, end.value))
    if (!res.ok) {
      if (res.status === 401) {
        // session expired mid-use (server-side is the real gate, see history_export() in
        // views.py) - flip back to the logged-out view rather than leaving the form up with a
        // dead error message next to it
        me.value = { authenticated: false, username: null }
      } else {
        downloadError.value = `Download failed: ${res.status} ${res.statusText}`
      }
      return
    }

    const blob = await res.blob()
    const match = res.headers.get('Content-Disposition')?.match(/filename="([^"]+)"/)
    const filename = match ? match[1] : `${selectedStation.value}.csv`

    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(link.href)
  } catch (e) {
    downloadError.value = (e as Error).message
  } finally {
    downloading.value = false
  }
}
</script>

<template>
  <div>
    <h4 class="mb-3">Historic data</h4>

    <div v-if="me === null" class="text-muted">Loading…</div>

    <div v-else-if="!me.authenticated" class="alert alert-info d-flex align-items-center gap-2">
      <i class="bi bi-lock"></i>
      <span>Log in to download historic data.</span>
      <a v-if="config?.keycloak_enabled" :href="loginUrl()" class="alert-link">Log in</a>
    </div>

    <div v-else>
      <div v-if="stationsError" class="alert alert-danger">Failed to load stations: {{ stationsError.message }}</div>

      <form class="row g-3 align-items-end" @submit.prevent="download">
        <div class="col-auto">
          <label for="history-station" class="form-label">Station</label>
          <select id="history-station" v-model="selectedStation" class="form-select" required>
            <option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option>
          </select>
        </div>
        <div class="col-auto">
          <label for="history-start" class="form-label">Start</label>
          <input id="history-start" v-model="start" type="date" class="form-control" required />
        </div>
        <div class="col-auto">
          <label for="history-end" class="form-label">End</label>
          <input id="history-end" v-model="end" type="date" class="form-control" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary" :disabled="downloading || !selectedStation">
            <i class="bi bi-download me-1"></i>
            {{ downloading ? 'Downloading…' : 'Download CSV' }}
          </button>
        </div>
      </form>

      <div v-if="downloadError" class="alert alert-danger mt-3">{{ downloadError }}</div>
    </div>
  </div>
</template>
