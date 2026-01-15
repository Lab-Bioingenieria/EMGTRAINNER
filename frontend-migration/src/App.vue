<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import AppSidebar from './components/common/AppSidebar.vue'

const route = useRoute()
// Optionally hide sidebar on login/public pages if any exist later
const showSidebar = true 
</script>

<template>
  <div class="app-layout">
     <AppSidebar v-if="route.name !== 'Home'" />
     <main class="main-wrapper">
        <RouterView />
     </main>
  </div>
</template>

<style>
/* Global Resets handled by style.css, here layout specifics */
body { margin: 0; background-color: #f8fafc; }

.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}
</style>