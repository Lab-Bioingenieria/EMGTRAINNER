<script setup lang="ts">
import { ref } from 'vue'
import {
  Bell,
  User,
  Search,
  Settings,
  LogOut
} from 'lucide-vue-next'

const props = defineProps<{
  title: string
  subtitle?: string
}>()

const isUserMenuOpen = ref(false)
const notificationCount = ref(3)

const toggleUserMenu = () => {
    isUserMenuOpen.value = !isUserMenuOpen.value
}
</script>

<template>
  <header class="top-header">
    <div class="header-left">
      <h1 class="header-title">{{ title }}</h1>
      <p v-if="subtitle" class="header-subtitle">{{ subtitle }}</p>
    </div>

    <div class="header-right">
      <!-- Search -->
      <div class="search-container hidden-sm">
        <Search class="search-icon" />
        <input type="text" placeholder="Buscar..." class="search-input" />
      </div>

      <!-- Notifications -->
      <button class="icon-btn relative">
        <Bell class="icon" />
        <span v-if="notificationCount > 0" class="badge-count">{{ notificationCount }}</span>
      </button>

      <!-- User Menu -->
      <div class="user-menu-container">
          <button class="icon-btn" @click="toggleUserMenu">
              <User class="icon" />
          </button>
          
          <div v-if="isUserMenuOpen" class="dropdown-menu">
              <div class="dropdown-label">Dr. García</div>
              <div class="dropdown-separator"></div>
              <button class="dropdown-item">Perfil</button>
              <button class="dropdown-item">Preferencias</button>
              <div class="dropdown-separator"></div>
              <button class="dropdown-item text-danger">
                  <LogOut class="icon-xs mr-2" /> Cerrar sesión
              </button>
          </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.top-header {
    height: 3.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #e2e8f0;
    background-color: white;
    padding: 0 1.5rem;
    position: sticky; top: 0; z-index: 10;
}

.header-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #0f172a;
    margin: 0;
}

.header-subtitle {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.search-container {
    position: relative;
    display: flex;
    align-items: center;
}
.search-icon {
    position: absolute;
    left: 0.75rem;
    width: 1rem;
    height: 1rem;
    color: #94a3b8;
}
.search-input {
    padding: 0.5rem 0.75rem 0.5rem 2.25rem;
    background-color: #f1f5f9;
    border: none;
    border-radius: 6px;
    font-size: 0.875rem;
    width: 250px;
    outline: none;
    color: #0f172a;
}
.search-input:focus {
    box-shadow: 0 0 0 2px #e2e8f0;
}

@media(max-width: 768px) {
    .hidden-sm { display: none; }
}

.icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    border-radius: 6px;
    border: none;
    background: transparent;
    cursor: pointer;
    color: #0f172a;
    transition: background-color 0.2s;
}
.icon-btn:hover {
    background-color: #f1f5f9;
}
.icon { width: 1.25rem; height: 1.25rem; }
.relative { position: relative; }

.badge-count {
    position: absolute;
    top: -2px; right: -2px;
    background-color: #0f172a;
    color: white;
    font-size: 0.65rem;
    width: 16px; height: 16px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 50%;
}

.user-menu-container { position: relative; }

.dropdown-menu {
    position: absolute;
    top: 100%; right: 0;
    margin-top: 0.5rem;
    width: 200px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    padding: 0.25rem;
    z-index: 50;
}

.dropdown-label {
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    font-weight: 600;
}

.dropdown-separator {
    height: 1px;
    background-color: #e2e8f0;
    margin: 0.25rem 0;
}

.dropdown-item {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0.5rem 0.75rem;
    text-align: left;
    background: none;
    border: none;
    font-size: 0.875rem;
    color: #0f172a;
    cursor: pointer;
    border-radius: 4px;
}
.dropdown-item:hover {
    background-color: #f1f5f9;
}
.text-danger { color: #ef4444; }
.icon-xs { width: 1rem; height: 1rem; }
</style>
