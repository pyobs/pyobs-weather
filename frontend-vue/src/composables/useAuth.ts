import { ref } from 'vue'
import { fetchJson, getCsrfToken, logoutUrl } from '../api/client'
import type { MeResponse } from '../api/types'

const me = ref<MeResponse | null>(null)
const loading = ref(false)

export function useAuth() {
  async function load() {
    if (loading.value) return
    loading.value = true
    try {
      me.value = await fetchJson<MeResponse>('me/')
    } catch {
      // anonymous is the safe default if the check itself fails
      me.value = { authenticated: false, username: null }
    } finally {
      loading.value = false
    }
  }

  // A real form POST + full-page navigation, not fetch(): pyobs-auth's LogoutView redirects to
  // Keycloak's RP-Initiated Logout endpoint for a Keycloak-established session, and that
  // redirect has to actually load in the browser for Keycloak to clear its own SSO cookies -
  // fetch() would follow it silently in the background instead.
  function logout() {
    const token = getCsrfToken()
    const form = document.createElement('form')
    form.method = 'POST'
    form.action = logoutUrl()
    form.style.display = 'none'
    if (token) {
      const input = document.createElement('input')
      input.type = 'hidden'
      input.name = 'csrfmiddlewaretoken'
      input.value = token
      form.appendChild(input)
    }
    document.body.appendChild(form)
    form.submit()
  }

  return { me, loading, load, logout }
}
