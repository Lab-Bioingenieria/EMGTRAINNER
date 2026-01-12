<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Activity,
  Brain,
  Users,
  Stethoscope,
  Hand,
  Settings,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
} from 'lucide-vue-next'

const route = useRoute()
const collapsed = ref(false)

const navigation = [
  {
    name: "AI Model Console",
    path: "/ai-console",
    icon: Brain,
    description: "Análisis del modelo",
  },
  {
    name: "Panel de Pacientes",
    path: "/dashboard",
    icon: Users,
    description: "Gestión y monitoreo",
  },
  {
    name: "Sesión Doctor",
    path: "/doctor",
    icon: Stethoscope,
    description: "Crear protocolos",
  },
  {
    name: "Sesión Paciente",
    path: "/patient",
    icon: Hand,
    description: "Entrenamiento",
  },
  {
    name: "Test",
    path: "/test",
    icon: ClipboardCheck,
    description: "Evaluación y calibración",
  },
]

// Auto-collapse logic based on route
watch(() => route.path, (newPath) => {
    if (newPath.startsWith('/patient')) {
        collapsed.value = true
    }
}, { immediate: true })

const sidebarClass = computed(() => collapsed.value ? 'collapsed' : 'expanded')
</script>

<template>
  <aside class="app-sidebar" :class="sidebarClass">
    <!-- Header -->
    <div class="sidebar-header">
      <router-link to="/" class="logo-link">
        <Activity class="logo-icon" />
        <span v-if="!collapsed" class="logo-text">MyoTrainer</span>
      </router-link>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navigation"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ 'active': route.path.startsWith(item.path) }"
      >
        <component :is="item.icon" class="nav-icon" />
        <div v-if="!collapsed" class="nav-content">
          <span class="nav-title">{{ item.name }}</span>
          <span class="nav-desc">{{ item.description }}</span>
        </div>
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <router-link to="/settings" class="nav-item settings-link" :class="{ 'active': route.path === '/settings' }">
        <Settings class="nav-icon" />
        <span v-if="!collapsed">Configuración</span>
      </router-link>
      
      <button class="collapse-btn" @click="collapsed = !collapsed">
        <ChevronRight v-if="collapsed" class="btn-icon" />
        <ChevronLeft v-else class="btn-icon" />
      </button>
    </div>
  </aside>
</template>

<style scoped>
/* Variables mimic standard token colors used across the app */
.app-sidebar {
    display: flex;
    flex-direction: column;
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
    height: 100vh;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    flex-shrink: 0;
    z-index: 50;
}

.expanded { width: 260px; }
.collapsed { width: 72px; } /* Slightly wider for better touch target */

/* Header */
.sidebar-header {
    height: 4rem;
    display: flex;
    align-items: center;
    padding: 0 1rem;
    margin-bottom: 0.5rem;
    /* border-bottom: 1px solid #f1f5f9; Optional: removed for cleaner look */
}

.collapsed .sidebar-header {
    justify-content: center;
    padding: 0;
}

.logo-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
    color: #0f172a;
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
}

.logo-icon {
    width: 2rem;
    height: 2rem;
    color: #2563eb;
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    padding: 0.25rem;
    border-radius: 8px;
    flex-shrink: 0;
}

.logo-text {
    font-weight: 700;
    font-size: 1.125rem;
    letter-spacing: -0.025em;
    color: #1e293b;
}

/* Nav */
.sidebar-nav {
    flex: 1;
    padding: 0 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
    overflow-y: auto;
    overflow-x: hidden;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.625rem 0.75rem;
    border-radius: 8px;
    text-decoration: none;
    color: #64748b;
    transition: all 0.2s ease;
    min-height: 48px;
    position: relative;
}

/* Collapsed Nav Item State */
.collapsed .nav-item {
    justify-content: center;
    padding: 0.625rem 0;
    gap: 0;
}

.nav-item:hover {
    background-color: #f8fafc;
    color: #0f172a;
}

.nav-item.active {
    background-color: #eff6ff;
    color: #2563eb;
}

/* Active indicator strip for premium feel */
.nav-item.active::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 24px;
    background-color: #2563eb;
    border-radius: 0 4px 4px 0;
    opacity: 0;
    transition: opacity 0.2s;
}

.expanded .nav-item.active::before {
    opacity: 1;
}

.nav-icon {
    width: 1.25rem;
    height: 1.25rem;
    flex-shrink: 0;
    transition: color 0.2s;
}

/* Tooltip behavior for collapsed state could be added here, 
   but for now we rely on the clean visual icon */

.nav-content {
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.nav-title {
    font-size: 0.9rem;
    font-weight: 500;
    line-height: 1.2;
}

.nav-desc {
    font-size: 0.75rem;
    opacity: 0.7;
    margin-top: 1px;
}

/* Footer */
.sidebar-footer {
    padding: 1rem 0.75rem;
    border-top: 1px solid #f1f5f9;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    background-color: #ffffff;
}

.collapse-btn {
    display: flex;
    align-items: center;
    justify-content: center; /* Always center the icon/content */
    padding: 0.5rem;
    border-radius: 8px;
    border: 1px solid #f1f5f9;
    background: white;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
    width: 100%;
}

.expanded .collapse-btn {
     justify-content: flex-end; /* Push icon to right if expanded */
     border: none; /* Cleaner look when expanded */
     background: transparent;
}

.collapsed .collapse-btn {
    border-color: transparent;
    background: #f8fafc;
}

.collapse-btn:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}
</style>
