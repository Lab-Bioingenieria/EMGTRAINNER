<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
    gesture: string
    isActive: boolean
}>()

// Mock visual logic: we will just show an SVG hand that highlights specific fingers based on gesture name
// Gestures: Palm Down, Palm Up, Close Hand, Open Hand, Close Pinch, Open Pinch, Rest Hand, Point Index
// We map these to visual states: 'closed', 'pinch', 'open', 'index'

const fingerState = computed(() => {
    const g = props.gesture.toLowerCase()
    
    // Explicit states
    if (g.includes('close hand') || g.includes('cerrar mano')) return 'closed'
    if (g.includes('close pinch') || g.includes('pinza cerrada')) return 'pinch'
    if (g.includes('open pinch') || g.includes('pinza abierta')) return 'pinch-open' 
    if (g.includes('point index') || g.includes('apuntar')) return 'index'
    
    // Default to open/relaxed for: Palm Down/Up, Open Hand, Rest Hand
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

/* Open Pinch - slightly separated but active color */
.pinch-open .index { transform: rotate(-5deg); fill: #60a5fa; }
.pinch-open .thumb { transform: rotate(5deg); fill: #60a5fa; }

/* Index Pointing */
.index .middle { height: 30px; y: 110px; fill: #64748b; }
.index .ring { height: 30px; y: 110px; fill: #64748b; }
.index .pinky { height: 30px; y: 110px; fill: #64748b; }
.index .thumb { width: 30px; x: 50px; fill: #64748b; }
.index .index { fill: #3b82f6; height: 80px; y: 50px; } /* Highlighted index */

.pulse .hand-svg { filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.5)); }

.viz-label {
    margin-top: 1.5rem; color: #94a3b8; font-size: 0.875rem;
}
</style>
