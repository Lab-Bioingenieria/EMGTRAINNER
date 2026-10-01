<script setup lang="ts">
/**
 * Representación continua (no un video de gesto discreto como
 * `PatientHandVisualization`): los dedos se doblan en proporción directa a
 * `activation` (0 = mano abierta, 1 = cerrada), el mismo valor que
 * `HandMirrorService` usa para mover la mano física.
 */
defineProps<{
  /** 0..1: que tan "cerrada" está la mano en este instante. */
  activation: number
  /** Si hay datos de sensor llegando ahora mismo. */
  connected: boolean
}>()
</script>

<template>
  <div class="mirror-hand">
    <div class="hand-rig" :class="{ idle: !connected }">
      <div class="palm">
        <div
          v-for="i in 5"
          :key="i"
          class="finger"
          :class="`finger-${i}`"
          :style="{ transform: `rotate(${activation * (i === 1 ? 55 : 80)}deg)` }"
        ></div>
      </div>
    </div>
    <p class="mirror-hand-label">
      <span class="status-dot" :class="{ active: connected }"></span>
      {{ connected ? `${Math.round(activation * 100)}% cerrada` : 'Sin datos del sensor' }}
    </p>
  </div>
</template>

<style scoped>
.mirror-hand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem 1rem;
}

.hand-rig {
  transition: opacity 0.3s;
}
.hand-rig.idle {
  opacity: 0.4;
}

.palm {
  position: relative;
  width: 160px;
  height: 130px;
  background: #1e293b;
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 8px;
  padding: 10px 14px 0;
}

.finger {
  width: 20px;
  height: 90px;
  background: linear-gradient(#93c5fd, #2563eb);
  border-radius: 10px 10px 4px 4px;
  transform-origin: bottom center;
  transition: transform 0.1s linear;
}

.finger-1 {
  height: 60px;
  background: linear-gradient(#fde68a, #d97706);
  align-self: flex-end;
  margin-bottom: -6px;
}

.mirror-hand-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #334155;
  font-size: 0.9rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #cbd5e1;
  transition: all 0.3s;
}
.status-dot.active {
  background-color: #22c55e;
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
}
</style>
