<script setup lang="ts">
import { AlertTriangle, Bell, Check } from 'lucide-vue-next'
</script>

<template>
  <div class="alerts-card">
      <div class="header">
          <h3>Alertas / Notificaciones</h3>
          <Bell class="icon text-muted" />
      </div>
      <div class="list">
          <div class="alert-item warning">
              <AlertTriangle class="icon-sm" />
              <div class="text">
                  <span class="title">Electrodo 2 inestable</span>
                  <span class="time">Hace 2m</span>
              </div>
          </div>
          <div class="alert-item success">
              <Check class="icon-sm" />
              <div class="text">
                  <span class="title">Calibración completada</span>
                  <span class="time">Hace 5m</span>
              </div>
          </div>
      </div>
  </div>
</template>

<style scoped>
.alerts-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem;
}
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
h3 { margin: 0; font-size: 1rem; font-weight: 600; color: #64748b; }
.icon { width: 1.25rem; height: 1.25rem; color: #94a3b8; }

.list { display: flex; flex-direction: column; gap: 0.75rem; }

.alert-item {
    display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem; border-radius: 6px; font-size: 0.875rem;
}
.alert-item.warning { background-color: #fffbeb; color: #b45309; }
.alert-item.success { background-color: #f0fdf4; color: #15803d; }

.icon-sm { width: 1rem; height: 1rem; margin-top: 2px; }
.text { display: flex; flex-direction: column; }
.title { font-weight: 500; }
.time { font-size: 0.75rem; opacity: 0.8; }
</style>
