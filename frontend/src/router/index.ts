import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/ai-console',
    name: 'AIConsole',
    component: () => import('../views/ai-console/AiConsoleView.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/dashboard/DashboardView.vue')
  },
  {
    path: '/doctor',
    name: 'DoctorSession',
    component: () => import('../views/doctor/DoctorSessionView.vue')
  },
  {
    path: '/patient',
    name: 'PatientSession',
    component: () => import('../views/patient/PatientSessionView.vue')
  },
  {
    path: '/patient/free',
    name: 'PatientFree',
    component: () => import('../views/patient/PatientFreeView.vue')
  },
  {
    path: '/patients',
    name: 'PatientsPanel',
    component: () => import('../views/patients/PatientsPanelView.vue')
  },
  {
    path: '/patients/:id',
    name: 'PatientDetails',
    component: () => import('../views/patients/PatientsDetailsView.vue')
  },
  {
    path: '/test',
    name: 'Test',
    component: () => import('../views/test/TestView.vue')
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router