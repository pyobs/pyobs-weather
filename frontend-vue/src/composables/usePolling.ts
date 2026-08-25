import { onUnmounted, ref, type Ref } from 'vue'

/** Poll a fetcher on a fixed interval, starting immediately. Safe to call per-component; cleanup
 * runs on unmount. */
export function usePolling<T>(
  fetcher: () => Promise<T>,
  intervalMs: number,
): {
  data: Ref<T | null>
  error: Ref<Error | null>
  refresh: () => Promise<void>
} {
  const data = ref<T | null>(null) as Ref<T | null>
  const error = ref<Error | null>(null)
  let timer: ReturnType<typeof setTimeout> | null = null
  let stopped = false

  async function refresh() {
    try {
      data.value = await fetcher()
      error.value = null
    } catch (e) {
      error.value = e as Error
    } finally {
      if (!stopped) timer = setTimeout(refresh, intervalMs)
    }
  }

  refresh()

  onUnmounted(() => {
    stopped = true
    if (timer) clearTimeout(timer)
  })

  return { data, error, refresh }
}
