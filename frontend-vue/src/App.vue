<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useConfig } from './composables/useConfig'
import CurrentValues from './components/CurrentValues.vue'

const route = useRoute()
const { config, load } = useConfig()

const sidebarOpen = ref(false)
const theme = ref<'light' | 'dark'>('light')

function currentTheme(): 'light' | 'dark' {
  const stored = localStorage.getItem('pyobs-theme')
  if (stored === 'dark' || stored === 'light') return stored
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme() {
  document.documentElement.setAttribute('data-bs-theme', theme.value)
}

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('pyobs-theme', theme.value)
  applyTheme()
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function closeSidebarOnNavigate() {
  if (window.innerWidth < 992) sidebarOpen.value = false
}

watch(
  () => route.fullPath,
  () => closeSidebarOnNavigate(),
)

onMounted(() => {
  theme.value = currentTheme()
  applyTheme()
  load()
})

watch(
  () => config.value?.title,
  (title) => {
    if (title) document.title = title
  },
)
</script>

<template>
  <!-- Mobile top navbar -->
  <nav
    class="d-lg-none d-flex align-items-center px-3 app-chrome border-bottom border-secondary-subtle sticky-top"
    style="height: 52px; z-index: 1043"
  >
    <i class="bi bi-cloud-sun text-primary me-2"></i>
    <span class="text-body fw-semibold me-auto">{{ config?.site ?? 'pyobs Weather' }}</span>
    <button class="btn btn-outline-secondary btn-sm me-2" @click="toggleTheme" title="Toggle light/dark mode" aria-label="Toggle theme">
      <i :class="theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill'"></i>
    </button>
    <button class="btn btn-outline-secondary btn-sm" @click="toggleSidebar" aria-label="Open sidebar">
      <i class="bi bi-list fs-5"></i>
    </button>
  </nav>

  <div class="sidebar-overlay" :class="{ active: sidebarOpen }" @click="toggleSidebar"></div>

  <div class="d-flex">
    <nav class="sidebar app-chrome" :class="{ open: sidebarOpen }" id="sidebar">
      <div class="p-3 border-bottom border-secondary-subtle d-flex d-lg-none align-items-center gap-2">
        <div class="me-auto">
          <div class="fw-semibold text-body lh-1">pyobs</div>
          <div class="text-muted" style="font-size: 0.7rem">Weather</div>
        </div>
        <button class="btn btn-sm btn-outline-secondary" @click="toggleSidebar" aria-label="Close sidebar">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <div class="p-2 flex-grow-1 overflow-auto">
        <div class="px-2 py-2">
          <RouterLink
            to="/"
            class="sidebar-link d-flex align-items-center gap-2 px-2 py-2"
            :class="{ active: route.name === 'overview' }"
          >
            <i class="bi bi-grid-1x2" style="font-size: 0.8rem"></i>
            Overview
          </RouterLink>
          <RouterLink
            to="/sensors"
            class="sidebar-link d-flex align-items-center gap-2 px-2 py-2"
            :class="{ active: route.name === 'sensors' }"
          >
            <i class="bi bi-thermometer-half" style="font-size: 0.8rem"></i>
            Sensors
          </RouterLink>
        </div>

        <div class="px-2 py-2 border-top border-secondary-subtle">
          <CurrentValues />
        </div>
      </div>

      <div class="p-2 border-top border-secondary-subtle">
        <button
          type="button"
          class="sidebar-link d-flex align-items-center gap-2 px-2 py-2 w-100 border-0 bg-transparent text-start"
          @click="toggleTheme"
        >
          <i :class="theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill'"></i>
          <span>Theme</span>
        </button>
      </div>

      <div class="p-2 border-top border-secondary-subtle text-muted" style="font-size: 0.75rem">
        pyobs-weather v{{ config?.version ?? '?' }}
        (<a href="https://github.com/pyobs/pyobs-weather" target="_blank" rel="noopener">GitHub</a>,
        <a href="https://hub.docker.com/repository/docker/thusser/pyobs-weather" target="_blank" rel="noopener">Docker</a>)
      </div>
    </nav>

    <main class="main-content flex-grow-1 p-3 p-lg-4">
      <RouterView />
    </main>
  </div>
</template>
