<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
    gesture: string
    isActive: boolean
}>()

// Mock visual logic: we will just show an SVG hand that highlights specific fingers based on gesture name
// Gestures: "Puño Cerrado", "Mano Abierta", "Flexión Muñeca", "Extensión Muñeca", "Pinza Fina"

const fingerState = computed(() => {
    const g = props.gesture.toLowerCase()
    if (g.includes('puño') || g.includes('closed')) return 'closed'
    if (g.includes('pinza') || g.includes('pinch')) return 'pinch'
    return 'open'
})
</script>

<template>
  <div class="hand-viz-container">
      <div class="hand-wrapper" :class="[fingerState, { pulse: isActive }]">
          <!-- Simplified Hand SVG Representation -->
          <svg viewBox="0 0 200 300" class="hand-svg">
              <!-- Palm -->
              <rect x="60" y="120" width="80" height="100" rx="20" class="palm" />
              <!-- Thumb -->
              <rect x="20" y="160" width="50" height="30" rx="15" class="thumb finger"  />
              <!-- Fingers -->
              <rect x="65" y="60" width="18" height="70" rx="9" class="finger index" />
              <rect x="90" y="50" width="20" height="80" rx="10" class="finger middle" />
              <rect x="115" y="60" width="18" height="70" rx="9" class="finger ring" />
              <rect x="140" y="80" width="16" height="50" rx="8" class="finger pinky" />
          </svg>
      </div>
      <p class="viz-label">Visualización en tiempo real</p>
  </div>
</template>

<style scoped>
.hand-viz-container {
    background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 2rem;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    border-top: 4px solid #3b82f6;
}
.hand-svg {
    width: 200px; height: 300px;
    fill: #e2e8f0; stroke: #cbd5e1; stroke-width: 2;
    transition: all 0.5s ease;
}
.palm { fill: #cbd5e1; }
.finger { transition: all 0.5s ease; transform-origin: center bottom; }

/* States */
.closed .finger { height: 30px; y: 110px; fill: #64748b; }
.closed .thumb { width: 30px; x: 50px; fill: #64748b; }

.pinch .index { transform: rotate(-15deg) translateY(20px); fill: #3b82f6; }
.pinch .thumb { transform: rotate(15deg) translateX(10px); fill: #3b82f6; }

.pulse .hand-svg { filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.5)); }

.viz-label {
    margin-top: 1.5rem; color: #94a3b8; font-size: 0.875rem;
}
</style>
