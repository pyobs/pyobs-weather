import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  base: command === 'build' ? '/static/frontend/dist/' : '/',
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
