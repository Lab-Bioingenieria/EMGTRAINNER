import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { authService } from '@/services/auth.service'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
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
    path: '/storage',
    name: 'Storage',
    component: () => import('../views/storage/StorageView.vue')
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

const PUBLIC_ROUTES = new Set(['Login'])

router.beforeEach((to) => {
  if (PUBLIC_ROUTES.has(to.name as string)) return true
  if (authService.isLoggedIn()) return true
  // Preserve the intended destination so Login can return the user to it.
  return { name: 'Login', query: { redirect: to.fullPath } }
})

export default router