<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/auth.service'

const route  = useRoute()
const router = useRouter()

const main = [
  { id: 'home',      path: '/',           label: 'Inicio',             sub: 'Panel general',       icon: 'layers' },
  { id: 'ai',        path: '/ai-console', label: 'AI Model Console',   sub: 'Análisis del modelo', icon: 'brain' },
  { id: 'dashboard', path: '/dashboard',  label: 'Panel de Pacientes', sub: 'Gestión y monitoreo', icon: 'users' },
  { id: 'storage',   path: '/storage',    label: 'Almacenamiento',     sub: 'Historial CSV',       icon: 'db' },
]

const session = [
  { id: 'doctor',  path: '/doctor',  label: 'Sesión Doctor',   sub: 'Crear protocolos', icon: 'steth' },
  { id: 'patient', path: '/patient', label: 'Sesión Paciente', sub: 'Entrenamiento',    icon: 'hand' },
  { id: 'test',    path: '/test',    label: 'Test & Calibrar', sub: 'Evaluación',       icon: 'adjust' },
]

const isActive = (path: string) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function logout() {
  authService.clearToken()
  router.push('/login')
}
</script>

<template>
  <aside class="sidebar">
    <!-- Brand -->
    <div class="sidebar-brand">
      <div class="brand-mark">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--bone-50)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 12h3l2-7 4 14 3-9 2 5h4"/>
        </svg>
      </div>
      <div>
        <div class="brand-name">EMGtrainner</div>
        <div class="brand-sub">sEMG · v2.4.1</div>
      </div>
    </div>

    <!-- Workspace section -->
    <div class="nav-section">Workspace</div>
    <div class="nav">
      <router-link
        v-for="item in main"
        :key="item.id"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <span class="nav-icon">
          <SidebarIcon :name="item.icon" />
        </span>
        <span class="nav-text">
          <span>{{ item.label }}</span>
          <span class="nav-sub">{{ item.sub }}</span>
        </span>
      </router-link>
    </div>

    <!-- Session section -->
    <div class="nav-section">Sesión</div>
    <div class="nav">
      <router-link
        v-for="item in session"
        :key="item.id"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <span class="nav-icon">
          <SidebarIcon :name="item.icon" />
        </span>
        <span class="nav-text">
          <span>{{ item.label }}</span>
          <span class="nav-sub">{{ item.sub }}</span>
        </span>
      </router-link>
    </div>

    <!-- Footer -->
    <div class="sidebar-foot">
      <div class="device-card">
        <div class="device-row">
          <span class="device-name">Ottobock bebionic</span>
          <span class="dot live" />
        </div>
        <div style="display:flex; justify-content:space-between; font-size:11px;">
          <span class="mono" style="color:var(--ink-4); letter-spacing:0.04em">BLDC · 6 DOF</span>
          <span class="mono" style="color:var(--ink-4)">82%</span>
        </div>
        <div class="bar pulse" style="height:4px"><span style="width:82%" /></div>
      </div>

      <button class="nav-item logout-btn" @click="logout">
        <span class="nav-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>
          </svg>
        </span>
        <span class="nav-text">
          <span>Cerrar sesión</span>
          <span class="nav-sub">Dra. C. Morales</span>
        </span>
      </button>
    </div>
  </aside>
</template>

<!-- icon component inline -->
<script lang="ts">
const icons: Record<string, string> = {
  layers:  '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/><path d="m3 18 9 5 9-5"/>',
  brain:   '<path d="M9 4a3 3 0 0 0-3 3v.5A2.5 2.5 0 0 0 4 10v.5A2.5 2.5 0 0 0 4 15v.5A2.5 2.5 0 0 0 6 18v.5A2.5 2.5 0 0 0 9 21V4Z"/><path d="M15 4a3 3 0 0 1 3 3v.5A2.5 2.5 0 0 1 20 10v.5A2.5 2.5 0 0 1 20 15v.5A2.5 2.5 0 0 1 18 18v.5A2.5 2.5 0 0 1 15 21V4Z"/>',
  users:   '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="8.5" r="3"/><path d="M16 14a5 5 0 0 1 5.5 6"/>',
  db:      '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
  steth:   '<path d="M5 3v6a5 5 0 0 0 10 0V3"/><path d="M5 3h2"/><path d="M13 3h2"/><path d="M10 14v3a4 4 0 0 0 8 0v-1"/><circle cx="18" cy="11" r="2"/>',
  hand:    '<path d="M9 11V5a1.5 1.5 0 0 1 3 0v6"/><path d="M12 11V4a1.5 1.5 0 0 1 3 0v7"/><path d="M15 11V5.5a1.5 1.5 0 0 1 3 0V14"/><path d="M9 11V7a1.5 1.5 0 0 0-3 0v7c0 4 3 7 6 7h1c3 0 5-2.5 5-5"/>',
  adjust:  '<path d="M4 6h10M4 12h7M4 18h13"/><circle cx="18" cy="6" r="2"/><circle cx="15" cy="12" r="2"/><circle cx="21" cy="18" r="2"/>',
}

import { defineComponent, h } from 'vue'

const SidebarIcon = defineComponent({
  props: { name: { type: String, required: true } },
  setup(props) {
    return () => h('svg', {
      width: 16, height: 16,
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '1.6',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      innerHTML: icons[props.name] ?? '',
    })
  }
})

export { SidebarIcon }
</script>

<style scoped>
.sidebar {
  background: var(--paper);
  border-right: 1px solid var(--bone-200);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100vh;
  width: 240px;
  flex-shrink: 0;
}

/* Brand */
.sidebar-brand {
  padding: 18px 18px 16px;
  display: flex; align-items: center; gap: 10px;
  border-bottom: 1px solid var(--bone-200);
}
.brand-mark {
  width: 28px; height: 28px;
  display: grid; place-items: center;
  background: var(--ink);
  border-radius: 6px;
}
.brand-name { font-weight: 600; font-size: 14.5px; letter-spacing: -0.01em; }
.brand-sub  { font-family: var(--font-mono); font-size: 10px; color: var(--ink-4); letter-spacing: 0.1em; text-transform: uppercase; }

/* Nav sections */
.nav-section {
  padding: 14px 12px 6px;
  font-family: var(--font-mono);
  font-size: 10.5px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ink-4);
}
.nav { display: flex; flex-direction: column; gap: 1px; padding: 0 8px; }

.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 10px;
  border-radius: 6px;
  color: var(--ink-3);
  font-size: 13.5px; font-weight: 500;
  text-align: left; width: 100%;
  text-decoration: none;
  transition: background 0.12s;
}
.nav-item:hover { background: var(--bone-100); color: var(--ink); }
.nav-item.active { background: var(--ink); color: var(--bone-50); }
.nav-item.active .nav-sub { color: var(--bone-300); }

.nav-icon {
  display: grid; place-items: center;
  width: 18px; height: 18px; opacity: 0.85;
  flex-shrink: 0;
}
.nav-text { display: flex; flex-direction: column; line-height: 1.2; }
.nav-sub  { font-family: var(--font-mono); font-size: 10px; color: var(--ink-4); letter-spacing: 0.04em; margin-top: 2px; }

/* Footer */
.sidebar-foot {
  margin-top: auto;
  padding: 12px;
  border-top: 1px solid var(--bone-200);
  display: flex; flex-direction: column; gap: 8px;
}
.device-card {
  padding: 10px 12px;
  background: var(--bone-100);
  border-radius: 8px;
  display: flex; flex-direction: column; gap: 6px;
}
.device-row { display: flex; align-items: center; justify-content: space-between; }
.device-name { font-size: 12px; font-weight: 500; }

.logout-btn { cursor: pointer; }
</style>
