<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{ isRunning: boolean }>()

// Simple sinusoidal mock data for 3 channels
const canvasRef = ref<HTMLCanvasElement | null>(null)

let animationId: number
let offset = 0

const draw = () => {
    const canvas = canvasRef.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Config
    const channels = 3
    const heightPerChannel = canvas.height / channels
    
    ctx.lineWidth = 2
    
    for(let i=0; i<channels; i++) {
        ctx.beginPath()
        ctx.strokeStyle = i === 0 ? '#3b82f6' : i === 1 ? '#10b981' : '#f59e0b'
        
        const centerY = (i * heightPerChannel) + (heightPerChannel / 2)
        
        for(let x=0; x < canvas.width; x++) {
            // Simulate signal: mix of sines + random noise
            // amplitude 0 if not running (flatline) except minor noise
            const isActive = props.isRunning
            const amplitude = isActive ? 20 : 2
            
            const signal = Math.sin((x + offset) * 0.05 + i) * amplitude 
                         + Math.random() * (isActive ? 5 : 1)
            
            if (x===0) ctx.moveTo(x, centerY + signal)
            else ctx.lineTo(x, centerY + signal)
        }
        ctx.stroke()
        
        // Separator lines
        if (i < channels -1) {
            ctx.fillStyle = '#e5e7eb'
            ctx.fillRect(0, (i+1)*heightPerChannel, canvas.width, 1)
        }
    }
    
    if (props.isRunning) {
        offset += 2
    }
    animationId = requestAnimationFrame(draw)
}

onMounted(() => {
    draw()
})

onUnmounted(() => {
    cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="emg-container">
      <div class="header">
          <h3>Señales sEMG en Tiempo Real</h3>
          <span class="badg" :class="isRunning ? 'live' : 'idle'">{{ isRunning ? 'LIVE' : 'STANDBY' }}</span>
      </div>
      <div class="canvas-wrapper">
          <canvas ref="canvasRef" width="600" height="300" class="canvas"></canvas>
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
.canvas { width: 100%; height: 100%; object-fit: contain; }

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}
</style>
