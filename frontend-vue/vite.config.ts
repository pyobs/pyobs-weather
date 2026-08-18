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
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
    },
  },
}))
