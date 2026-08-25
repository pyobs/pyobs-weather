import { createRouter, createWebHistory } from 'vue-router'
import { getRootUrl } from '../api/client'
import OverviewView from '../views/OverviewView.vue'
import SensorsView from '../views/SensorsView.vue'

const router = createRouter({
  history: createWebHistory(getRootUrl()),
  routes: [
    { path: '/', name: 'overview', component: OverviewView },
    { path: '/sensors', name: 'sensors', component: SensorsView },
  ],
})

export default router
