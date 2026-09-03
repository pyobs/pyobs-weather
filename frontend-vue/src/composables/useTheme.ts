import { onUnmounted, ref, type Ref } from 'vue'

/** Tracks the app's `data-bs-theme` attribute (set by `App.vue`'s theme toggle) via a
 * `MutationObserver`, so components can react when the user switches theme without needing
 * their own copy of the toggle state. */
export function useTheme(): { theme: Ref<'light' | 'dark'> } {
  const root = document.documentElement
  const theme = ref<'light' | 'dark'>(root.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light') as Ref<
    'light' | 'dark'
  >

  const observer = new MutationObserver(() => {
    theme.value = root.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light'
  })
  observer.observe(root, { attributes: true, attributeFilter: ['data-bs-theme'] })

  onUnmounted(() => observer.disconnect())

  return { theme }
}
