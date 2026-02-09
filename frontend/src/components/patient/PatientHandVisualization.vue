<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
    gesture: string
    isActive: boolean
}>()

const currentFrame = ref(1)
let intervalId: number | null = null

// Random stickiness for Spherical to avoid flickering between Cube/Ball on re-renders if not desired,
// but since we want "can show two", let's randomize when the gesture *changes* to Spherical.
// We'll use a ref that updates whenever the gesture changes.
const sphericalVariant = ref<'Cube' | 'Ball'>('Ball')

watch(() => props.gesture, (newVal) => {
    if (newVal.toLowerCase().includes('esférico') || newVal.toLowerCase().includes('spherical')) {
        sphericalVariant.value = Math.random() > 0.5 ? 'Cube' : 'Ball'
    }
}, { immediate: true })

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

interface MediaSource {
    type: 'video' | 'image';
    src: string;
}

const gestureMedia = computed((): MediaSource => {
    const g = props.gesture.toLowerCase().trim()
    
    // Video Mappings
    if (g.includes('cerrar') || g.includes('close')) return { type: 'video', src: '/movements_video/Close.mp4' }
    if (g.includes('abrir') || g.includes('open')) return { type: 'video', src: '/movements_video/Open.mp4' }
    if (g.includes('pinza') || g.includes('pinch')) return { type: 'video', src: '/movements_video/Pinch.mp4' }
    if (g.includes('cilindrico') || g.includes('cylindrical')) return { type: 'video', src: '/movements_video/Cylindrical.mp4' }
    
    // New Video Mappings (AVI)
    if (g.includes('apuntar') || g.includes('point')) return { type: 'video', src: '/movements_video/Point.mp4' }
    if (g.includes('arriba') || g.includes('like')) return { type: 'video', src: '/movements_video/Like.mp4' }

    // Spherical - Random choice
    if (g.includes('esférico') || g.includes('spherical')) return { type: 'video', src: '/movements_video/Spherical.mp4'}

    // Image Fallbacks (Rest, etc.)
    let dir = 'rest'
    let file = 'Rest'

    if (g.includes('reposo') || g.includes('rest')) { dir = 'rest'; file = 'Rest' }
    else if (g.includes('abajo') || g.includes('down')) { dir = 'salute'; file = 'Salute' }
    
    return { 
        type: 'image', 
        src: `/movements/${dir}/DynaHand-${file}-${currentFrame.value}.png`
    }
})
</script>

<template>
  <div class="hand-viz-container">
      <div class="viz-content" :class="{ 'active-pulse': isActive }">
          <transition name="fade" mode="out-in">
              <!-- Video Player -->
              <video 
                v-if="gestureMedia.type === 'video'"
                :key="gestureMedia.src"
                :src="gestureMedia.src"
                autoplay 
                loop 
                muted 
                playsinline
                class="hand-media"
              ></video>

              <!-- Image Fallback -->
              <img 
                v-else
                :key="gestureMedia.src"
                :src="gestureMedia.src" 
                alt="Hand Visualization" 
                class="hand-media"
              />
          </transition>
      </div>
      <p class="viz-label">
          <span class="status-dot" :class="{ active: isActive }"></span>
          Visualización en tiempo real
          <span v-if="gestureMedia.type === 'video'" class="badge-mini">VIDEO</span>
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
    overflow: hidden;
    border-radius: 8px;
}

.hand-media {
    max-width: 100%;
    max-height: 550px;
    object-fit: contain;
    filter: drop-shadow(0 10px 15px rgba(59, 130, 246, 0.15));
    transition: transform 0.3s ease;
}

.active-pulse .hand-media {
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

.badge-mini {
    font-size: 0.65rem;
    background: #eff6ff;
    color: #3b82f6;
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid #dbeafe;
    font-weight: 600;
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
