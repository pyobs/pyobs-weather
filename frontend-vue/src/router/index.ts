import { createRouter, createWebHistory } from 'vue-router'
import OverviewView from '../views/OverviewView.vue'
import SensorsView from '../views/SensorsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'overview', component: OverviewView },
    { path: '/sensors', name: 'sensors', component: SensorsView },
  ],
})

export default router
