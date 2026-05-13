<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppSidebar from './components/common/AppSidebar.vue'

const route = useRoute()
const isLoginPage = computed(() => route.name === 'Login')
const isHomePage  = computed(() => route.name === 'Home')
const showSidebar = computed(() => !isLoginPage.value && !isHomePage.value)
</script>

<template>
  <RouterView v-if="isLoginPage" />
  <div v-else-if="isHomePage" class="home-shell">
    <main class="home-main">
      <RouterView />
    </main>
  </div>
  <div v-else class="shell">
    <AppSidebar />
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style>
.home-shell {
  height: 100vh;
  width: 100vw;
  background: var(--bone-50);
  display: flex;
  flex-direction: column;
}
.home-main {
  flex: 1;
  overflow-y: auto;
}
.main-content {
  overflow-y: auto;
  height: 100vh;
}
</style>
