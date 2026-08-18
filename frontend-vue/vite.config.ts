import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  // ROOT_URL is only known at container runtime (see pyobs_weather/settings.py), not at image
  // build time, so bake in a placeholder that pyobs_weather/frontend/views.py rewrites to the
  // real STATIC_URL when it serves index.html.
  base: command === 'build' ? '/__PYOBS_STATIC_BASE__/frontend/dist/' : '/',
  build: {
    outDir: '../pyobs_weather/frontend/static/frontend/dist',
    emptyOutDir: true,
  },
  experimental: {
    // CSS asset-to-asset references (e.g. bootstrap-icons' @font-face url()) resolve relative to
    // the stylesheet's own URL, not the page's, so they don't need the ROOT_URL placeholder —
    // and Django only rewrites the placeholder in index.html, not in served CSS. Keep those
    // relative; JS/HTML references still need the absolute placeholder.
    renderBuiltUrl(_filename, { hostType }) {
      if (hostType === 'css') return { relative: true }
      return undefined
    },
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
    },
  },
}))
