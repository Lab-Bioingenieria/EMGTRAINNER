<script setup lang="ts">
import { computed } from 'vue'
import { AlertTriangle, Bell, Check } from 'lucide-vue-next'
import { useSessionStore } from '../../stores/session'

const store = useSessionStore()

interface AlertItem {
  key: string
  kind: 'warning' | 'success'
  title: string
}

/**
 * Antes esta tarjeta mostraba dos alertas fijas en el HTML ("Electrodo 2
 * inestable", "Calibración completada") que nunca cambiaban, sin importar
 * lo que pasara con los sensores. Ahora se recalculan a partir del estado
 * real de la sesion (`store.emgSignals` / `store.sensorsOnline`), que ya se
 * refresca cada ~1.5s con datos reales del backend (ver refreshSensors en
 * session.ts) - asi esta lista cambia de verdad en vivo.
 */
const alerts = computed<AlertItem[]>(() => {
  const items: AlertItem[] = []

  if (!store.sensorsOnline) {
    items.push({
      key: 'device-offline',
      kind: 'warning',
      title: 'Dispositivo ESP32 sin conexión',
    })
    return items
  }

  const inactive = store.emgSignals.filter((s) => s.status !== 'active')
  if (inactive.length > 0) {
    for (const signal of inactive) {
      items.push({
        key: `channel-${signal.id}`,
        kind: 'warning',
        title: `${signal.name} sin señal`,
      })
    }
  } else {
    items.push({
      key: 'all-active',
      kind: 'success',
      title: 'Las 3 señales sEMG están activas',
    })
  }

  if (store.phase === 'running' && !store.sensorsOnline) {
    items.push({
      key: 'signal-lost-running',
      kind: 'warning',
      title: 'Se perdió la señal durante la sesión en curso',
    })
  }

  return items
})
</script>

<template>
  <div class="alerts-card">
      <div class="header">
          <h3>Alertas / Notificaciones</h3>
          <Bell class="icon text-muted" />
      </div>
      <div class="list">
          <div v-for="alert in alerts" :key="alert.key" class="alert-item" :class="alert.kind">
              <AlertTriangle v-if="alert.kind === 'warning'" class="icon-sm" />
              <Check v-else class="icon-sm" />
              <div class="text">
                  <span class="title">{{ alert.title }}</span>
                  <span class="time">En vivo</span>
              </div>
          </div>
          <div v-if="alerts.length === 0" class="alert-item empty">
              <span class="title text-muted">Sin novedades</span>
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
.alert-item.empty { color: #94a3b8; }

.icon-sm { width: 1rem; height: 1rem; margin-top: 2px; }
.text { display: flex; flex-direction: column; }
.title { font-weight: 500; }
.time { font-size: 0.75rem; opacity: 0.8; }
</style>
