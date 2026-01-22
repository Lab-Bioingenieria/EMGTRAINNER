<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
    gesture: string
    isActive: boolean
}>()

const currentFrame = ref(1)
let intervalId: number | null = null

const startAnimation = () => {
    if (intervalId) clearInterval(intervalId)
    intervalId = window.setInterval(() => {
        currentFrame.value = currentFrame.value === 1 ? 2 : 1
    }, 800) // Toggle every 800ms
}

onMounted(() => {
    startAnimation()
})

onUnmounted(() => {
    if (intervalId) clearInterval(intervalId)
})

const gestureMapping = computed(() => {
    const g = props.gesture.toLowerCase().trim()
    
    // Mapping logic based on directory structure
    // Directories: Pinch, close, like, open, point, rest, salute
    // Files pattern: /movements/[dir]/DynaHand-[Capitalized]-1.png
    
    if (g.includes('cerrar') || g.includes('close')) return { dir: 'close', file: 'Close' }
    if (g.includes('abrir') || g.includes('open')) return { dir: 'open', file: 'Open' }
    if (g.includes('pinza') || g.includes('pinch')) return { dir: 'Pinch', file: 'Pinch' }
    if (g.includes('apuntar') || g.includes('point')) return { dir: 'point', file: 'Point' }
    if (g.includes('reposo') || g.includes('rest')) return { dir: 'rest', file: 'Rest' }
    if (g.includes('abajo') || g.includes('down')) return { dir: 'salute', file: 'Salute' } // Approximation
    if (g.includes('arriba') || g.includes('up')) return { dir: 'like', file: 'Like' }   // Approximation (Thumb Up?)
    
    return { dir: 'rest', file: 'Rest' } // Default
})

const imagePath = computed(() => {
    const { dir, file } = gestureMapping.value
    return `/movements/${dir}/DynaHand-${file}-${currentFrame.value}.png`
})
</script>

<template>
  <div class="hand-viz-container">
      <div class="viz-content" :class="{ 'active-pulse': isActive }">
          <transition name="fade" mode="out-in">
              <img 
                :key="imagePath"
                :src="imagePath" 
                alt="Hand Visualization" 
                class="hand-image"
              />
          </transition>
      </div>
      <p class="viz-label">
          <span class="status-dot" :class="{ active: isActive }"></span>
          Visualización en tiempo real
      </p>
  </div>
</template>

<style scoped>
.hand-viz-container {
    background: white; 
    border: 1px solid #e2e8f0; 
    border-radius: 16px; 
    padding: 2rem;
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    justify-content: center;
    border-top: 4px solid #3b82f6;
    height: 100%;
    min-height: 600px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.viz-content {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    position: relative;
}

.hand-image {
    max-width: 100%;
    max-height: 550px;
    object-fit: contain;
    filter: drop-shadow(0 10px 15px rgba(59, 130, 246, 0.15));
    transition: transform 0.3s ease;
}

.active-pulse .hand-image {
    filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.4));
    transform: scale(1.02);
}

.viz-label {
    margin-top: 1.5rem; 
    color: #64748b; 
    font-size: 0.875rem; 
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
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

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0.8;
}
</style>
