<script setup lang="ts">
import { ref } from 'vue'
import EmgSerialPlotter from '../common/EmgSerialPlotter.vue'
import { buildAuthenticatedWebSocketUrl } from '@/lib/websocket'

defineProps<{ isRunning: boolean }>()

const wsUrl = buildAuthenticatedWebSocketUrl('/v1/monitoring/sensor/ws/emg-stream')
const isConnected = ref(false)
</script>

<template>
  <div class="emg-container">
      <div class="header">
          <h3>Señales sEMG en Tiempo Real</h3>
          <span class="badg" :class="isConnected ? 'live' : 'idle'">{{ isConnected ? 'LIVE' : 'SIN SEÑAL' }}</span>
      </div>
      <div class="canvas-wrapper">
          <EmgSerialPlotter
            :websocket-url="wsUrl"
            :is-running="isRunning"
            @connection-change="isConnected = $event"
          />
      </div>
  </div>
</template>

<style scoped>
.emg-container {
    background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem;
    height: 100%; display: flex; flex-direction: column;
}
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
h3 { margin: 0; font-size: 1.1rem; font-weight: 600; color: #0f172a; }

.badg { padding: 2px 8px; font-size: 0.75rem; border-radius: 4px; font-weight: 600; }
.live { background-color: #ef4444; color: white; animation: pulse 1.5s infinite; }
.idle { background-color: #f1f5f9; color: #64748b; }

.canvas-wrapper {
    flex: 1; min-height: 200px; width: 100%; border: 1px solid #f1f5f9; background-color: #fafafa; border-radius: 4px;
    overflow: hidden;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}
</style>
