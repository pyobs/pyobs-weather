import { ref } from 'vue'
import { fetchJson, setRootUrl } from '../api/client'
import type { ConfigResponse } from '../api/types'

const config = ref<ConfigResponse | null>(null)
const loading = ref(false)
const error = ref<Error | null>(null)

export function useConfig() {
  async function load() {
    if (config.value || loading.value) return
    loading.value = true
    error.value = null
    try {
      const c = await fetchJson<ConfigResponse>('config/')
      setRootUrl(c.root_url)
      config.value = c
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  return { config, loading, error, load }
}
