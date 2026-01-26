<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
  websocketUrl: string
  isRunning?: boolean
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)
const isConnected = ref(false)
const socket = ref<WebSocket | null>(null)

// Data buffers for 3 sensors
const bufferLength = 500
const dataBuffer = ref<{s1: number[], s2: number[], s3: number[]}>({
    s1: new Array(bufferLength).fill(0),
    s2: new Array(bufferLength).fill(0),
    s3: new Array(bufferLength).fill(0)
})

let animationFrameId: number = 0
const colors = ['#e11d48', '#2563eb', '#16a34a'] // Red, Blue, Green in hex (Tailwind colors)

const connectWebSocket = () => {
    if (socket.value) socket.value.close()
    
    try {
        socket.value = new WebSocket(props.websocketUrl)
        
        socket.value.onopen = () => {
            isConnected.value = true
            console.log("WS Connected")
        }
        
        socket.value.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                // Assuming data is { s1: 123, s2: 456, s3: 789 } or { sensors: [123, 456, 789] }
                // Adjust parsing based on actual backend format.
                // Looking at typical simple ESP32 streams, it's often keys like 'emg1', 'ch1', or array.
                // I will safeguard multiple formats.
                
                let s1 = 0, s2 = 0, s3 = 0
                
                if (Array.isArray(data)) {
                    s1 = data[0] || 0
                    s2 = data[1] || 0
                    s3 = data[2] || 0
                } else if (data.sensors && Array.isArray(data.sensors)) {
                     s1 = data.sensors[0] || 0
                     s2 = data.sensors[1] || 0
                     s3 = data.sensors[2] || 0
                } else {
                    // Try common keys
                    s1 = data.s1 || data.emg1 || data.ch1 || data.channel1 || 0
                    s2 = data.s2 || data.emg2 || data.ch2 || data.channel2 || 0
                    s3 = data.s3 || data.emg3 || data.ch3 || data.channel3 || 0
                }
                
                // Shift and push
                dataBuffer.value.s1.shift()
                dataBuffer.value.s1.push(s1)
                
                dataBuffer.value.s2.shift()
                dataBuffer.value.s2.push(s2)
                
                dataBuffer.value.s3.shift()
                dataBuffer.value.s3.push(s3)
                
            } catch (e) {
                console.error("Error parsing WS data", e)
            }
        }
        
        socket.value.onclose = () => {
            isConnected.value = false
            console.log("WS Closed")
        }
        
    } catch (e) {
        console.error("WS Connection failed", e)
    }
}

const draw = () => {
    const canvas = canvasRef.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    const width = canvas.width
    const height = canvas.height
    
    // Clear
    ctx.clearRect(0, 0, width, height)
    
    // Draw Grid (optional, for "Serial Plotter" look)
    ctx.strokeStyle = '#e2e8f0'
    ctx.lineWidth = 1
    ctx.beginPath()
    for (let i = 0; i < width; i += 50) { ctx.moveTo(i, 0); ctx.lineTo(i, height); }
    for (let i = 0; i < height; i += 50) { ctx.moveTo(0, i); ctx.lineTo(width, i); }
    ctx.stroke()
    
    // Draw Sensors
    const plotLine = (data: number[], color: string) => {
        ctx.beginPath()
        ctx.strokeStyle = color
        ctx.lineWidth = 2
        
        // Normalize roughly? Or just raw logic. 
        // ESP32 ADC is usually 0-4095. Let's scale to height.
        // If unknown, we might clip. Let's assume 0-4095 for now and auto-scale if needed?
        // Let's use a fixed scale 0-4095 mapped to canvas height for stability.
        
        const step = width / bufferLength
        
        data.forEach((val, index) => {
            const x = index * step
            // Invert Y because canvas 0 is top
            const y = height - (val / 4096) * height 
            
            if (index === 0) ctx.moveTo(x, y)
            else ctx.lineTo(x, y)
        })
        
        ctx.stroke()
    }
    
    plotLine(dataBuffer.value.s1, colors[0])
    plotLine(dataBuffer.value.s2, colors[1])
    plotLine(dataBuffer.value.s3, colors[2])
    
    animationFrameId = requestAnimationFrame(draw)
}

const resizeCanvas = () => {
    if (containerRef.value && canvasRef.value) {
        canvasRef.value.width = containerRef.value.clientWidth
        canvasRef.value.height = containerRef.value.clientHeight
    }
}

watch(() => props.isRunning, (newVal) => {
    if (newVal) {
      if (!isConnected.value) connectWebSocket()
    } else {
      if (socket.value) socket.value.close()
    }
})

onMounted(() => {
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
    draw() // Start animation loop
    
    // Auto-start if prop is true
    if (props.isRunning) connectWebSocket()
})

onUnmounted(() => {
    if (animationFrameId) cancelAnimationFrame(animationFrameId)
    window.removeEventListener('resize', resizeCanvas)
    if (socket.value) socket.value.close()
})

</script>

<template>
  <div class="plotter-container" ref="containerRef">
    <canvas ref="canvasRef"></canvas>
    
    <div class="legend" v-if="isConnected">
        <div class="legend-item"><span class="dot" :style="{background: colors[0]}"></span> Sensor 1</div>
        <div class="legend-item"><span class="dot" :style="{background: colors[1]}"></span> Sensor 2</div>
        <div class="legend-item"><span class="dot" :style="{background: colors[2]}"></span> Sensor 3</div>
    </div>
    
    <div class="overlay-msg" v-if="!isConnected">
        <p>Esperando conexión...</p>
    </div>
  </div>
</template>

<style scoped>
.plotter-container {
    width: 100%;
    height: 100%;
    min-height: 300px;
    background-color: #fff;
    position: relative;
    border-radius: 8px;
    overflow: hidden;
}

canvas {
    display: block;
    width: 100%;
    height: 100%;
}

.legend {
    position: absolute;
    top: 10px;
    right: 10px;
    display: flex;
    gap: 15px;
    background: rgba(255, 255, 255, 0.8);
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    color: #475569;
    border: 1px solid #e2e8f0;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.overlay-msg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(248, 250, 252, 0.5);
    color: #64748b;
    font-size: 0.9rem;
}
</style>
