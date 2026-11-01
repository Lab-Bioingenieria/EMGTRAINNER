import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { authGuard, roleGuard } from './guards'

// `meta.role` is what keeps the doctor and patient interfaces separate at
// the routing level — see router/guards.ts (roleGuard) for how it's
// enforced, and core/fastapi/dependencies/role.py on the backend for the
// matching server-side check.
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
    meta: { role: 'doctor' },
    component: () => import('../views/ai-console/AiConsoleView.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    meta: { role: 'doctor' },
    component: () => import('../views/dashboard/DashboardView.vue')
  },
  {
    path: '/doctor',
    name: 'DoctorSession',
    meta: { role: 'doctor' },
    component: () => import('../views/doctor/DoctorSessionView.vue')
  },
  {
    path: '/patient',
    name: 'PatientSession',
    meta: { role: 'patient' },
    component: () => import('../views/patient/PatientSessionView.vue')
  },
  {
    path: '/patient/free',
    name: 'PatientFree',
    meta: { role: 'patient' },
    component: () => import('../views/patient/PatientFreeView.vue')
  },
  {
    path: '/patient/mirror',
    name: 'PatientMirror',
    meta: { role: 'patient' },
    component: () => import('../views/patient/PatientMirrorView.vue')
  },
  {
    path: '/patients',
    name: 'PatientsPanel',
    meta: { role: 'doctor' },
    component: () => import('../views/patients/PatientsPanelView.vue')
  },
  {
    path: '/patients/:id',
    name: 'PatientDetails',
    meta: { role: 'doctor' },
    component: () => import('../views/patients/PatientsDetailsView.vue')
  },
  {
    path: '/storage',
    name: 'Storage',
    meta: { role: 'doctor' },
    component: () => import('../views/storage/StorageView.vue')
  },
  {
    path: '/test',
    name: 'Test',
    meta: { role: 'doctor' },
    component: () => import('../views/test/TestView.vue')
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  const authResult = authGuard(to)
  if (authResult !== true) return authResult
  return roleGuard(to)
})

export default router