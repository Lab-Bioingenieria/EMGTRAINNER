<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps<{
  /** URL, or a function returning a fresh one (so reconnects use a new JWT). */
  websocketUrl: string | (() => string)
  isRunning?: boolean
}>()

/** true = socket open AND samples are arriving. */
const emit = defineEmits<{ 'connection-change': [connected: boolean] }>()

// ---- Configuration -------------------------------------------------------
const CHANNELS = 3
const WINDOW_MS = 6000        // visible time span
const CAPACITY = 4096         // ring size (>> samples in WINDOW_MS)
const STALE_MS = 1500         // no samples for this long => "sin datos"
const RECONNECT_MIN_MS = 500
const RECONNECT_MAX_MS = 5000
const COLORS = ['#e11d48', '#2563eb', '#16a34a']
const PAD = { l: 48, r: 10, t: 10, b: 22 }

// ---- UI state (reactive, changes rarely) ---------------------------------
const canvasRef = ref<HTMLCanvasElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)
const isOpen = ref(false)
const hasSignal = ref(false)

// ---- Sample storage: plain typed arrays, deliberately NOT reactive --------
// Pushing hundreds of samples per second into Vue reactive arrays (with
// shift()) is what used to make the plot stutter.
const times = new Float64Array(CAPACITY)
const values = Array.from({ length: CHANNELS }, () => new Float32Array(CAPACITY))
let head = 0
let count = 0
let lastSampleAt = 0

// Auto-scale state
let yLo = 0
let yHi = 1

// Connection state
let socket: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | undefined
let retry = 0

// Canvas state
let rafId = 0
let resizeObserver: ResizeObserver | null = null
let cssW = 0
let cssH = 0
let dpr = 1

// ---- Helpers ---------------------------------------------------------------
function setSignal(v: boolean) {
  if (hasSignal.value !== v) {
    hasSignal.value = v
    emit('connection-change', v)
  }
}

function toNumber(x: unknown): number {
  if (typeof x === 'number') return x
  if (typeof x === 'string' && x.trim() !== '') return Number(x)
  return NaN
}

/** Accepts the payload shapes the backend has used: dc0..2, emg1..3, arrays. */
function extractSample(data: any): number[] | null {
  if (data == null || typeof data !== 'object' || data.error) return null

  let raw: unknown[]
  if (Array.isArray(data)) raw = data
  else if (Array.isArray(data.sensors)) raw = data.sensors
  else {
    raw = [0, 1, 2].map((i) => data[`dc${i}`] ?? data[`s${i + 1}`] ?? data[`emg${i + 1}`] ?? data[`ch${i + 1}`])
  }

  const nums = raw.slice(0, CHANNELS).map(toNumber)
  if (!nums.some(Number.isFinite)) return null
  while (nums.length < CHANNELS) nums.push(NaN)
  return nums.map((n) => (Number.isFinite(n) ? n : 0))
}

function pushSample(sample: number[]) {
  const now = performance.now()
  times[head] = now
  for (let c = 0; c < CHANNELS; c++) values[c][head] = sample[c]
  head = (head + 1) % CAPACITY
  if (count < CAPACITY) count++
  lastSampleAt = now
}

function resetBuffers() {
  head = 0
  count = 0
  yLo = 0
  yHi = 1
}

// ---- WebSocket lifecycle ---------------------------------------------------
function resolveUrl(): string {
  return typeof props.websocketUrl === 'function' ? props.websocketUrl() : props.websocketUrl
}

function dropSocket() {
  const s = socket
  socket = null // handlers below ignore any socket that is not the current one
  isOpen.value = false
  if (s) {
    try {
      s.close()
    } catch {
      /* already closed */
    }
  }
}

function scheduleReconnect() {
  clearTimeout(reconnectTimer)
  const delay = Math.min(RECONNECT_MIN_MS * 2 ** retry, RECONNECT_MAX_MS)
  retry++
  reconnectTimer = setTimeout(() => {
    if (props.isRunning) connect()
  }, delay)
}

function connect() {
  clearTimeout(reconnectTimer)
  dropSocket()

  let ws: WebSocket
  try {
    ws = new WebSocket(resolveUrl())
  } catch (e) {
    console.error('EMG plotter: cannot open WebSocket', e)
    scheduleReconnect()
    return
  }
  socket = ws

  ws.onopen = () => {
    if (socket !== ws) return
    isOpen.value = true
    retry = 0
  }

  ws.onmessage = (event) => {
    if (socket !== ws) return
    let parsed: unknown
    try {
      parsed = JSON.parse(event.data)
    } catch {
      return // ignore malformed frame instead of killing the stream
    }
    const sample = extractSample(parsed)
    if (!sample) return
    pushSample(sample)
    setSignal(true)
  }

  ws.onerror = () => {
    if (socket === ws) ws.close()
  }

  ws.onclose = () => {
    if (socket !== ws) return
    socket = null
    isOpen.value = false
    setSignal(false)
    if (props.isRunning) scheduleReconnect()
  }
}

function disconnect() {
  clearTimeout(reconnectTimer)
  retry = 0
  dropSocket()
  setSignal(false)
}

// ---- Rendering ----------------------------------------------------------------
function niceLabel(v: number, span: number): string {
  if (span >= 100) return v.toFixed(0)
  if (span >= 10) return v.toFixed(1)
  if (span >= 1) return v.toFixed(2)
  return v.toFixed(3)
}

function draw() {
  rafId = requestAnimationFrame(draw)

  const canvas = canvasRef.value
  if (!canvas || !cssW || !cssH) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const now = performance.now()
  if (hasSignal.value && now - lastSampleAt > STALE_MS) setSignal(false)

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, cssW, cssH)

  const plotW = cssW - PAD.l - PAD.r
  const plotH = cssH - PAD.t - PAD.b
  if (plotW <= 0 || plotH <= 0) return

  const t0 = now - WINDOW_MS

  // Newest-first walk to find how many samples fall inside the window.
  let n = 0
  while (n < count) {
    const idx = (head - 1 - n + CAPACITY) % CAPACITY
    if (times[idx] < t0) break
    n++
  }
  const start = (head - n + CAPACITY) % CAPACITY

  // Auto-scale: expand fast, shrink slowly so the trace does not "breathe".
  if (n > 0) {
    let lo = Infinity
    let hi = -Infinity
    for (let c = 0; c < CHANNELS; c++) {
      const arr = values[c]
      for (let i = 0; i < n; i++) {
        const v = arr[(start + i) % CAPACITY]
        if (v < lo) lo = v
        if (v > hi) hi = v
      }
    }
    if (lo >= 0) lo = 0
    let span = hi - lo
    if (span < 1e-6) span = 1e-6
    const targetHi = hi + span * 0.15
    const targetLo = lo < 0 ? lo - span * 0.15 : 0
    yHi += (targetHi - yHi) * (targetHi > yHi ? 0.6 : 0.04)
    yLo += (targetLo - yLo) * (targetLo < yLo ? 0.6 : 0.04)
  }
  const ySpan = Math.max(yHi - yLo, 1e-6)

  // Grid + axis labels
  ctx.font = '11px system-ui, sans-serif'
  ctx.fillStyle = '#94a3b8'
  ctx.strokeStyle = '#e2e8f0'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.textAlign = 'right'
  ctx.textBaseline = 'middle'
  for (let i = 0; i <= 4; i++) {
    const y = PAD.t + plotH - (i / 4) * plotH
    ctx.moveTo(PAD.l, Math.round(y) + 0.5)
    ctx.lineTo(PAD.l + plotW, Math.round(y) + 0.5)
    ctx.fillText(niceLabel(yLo + (i / 4) * ySpan, ySpan), PAD.l - 6, y)
  }
  ctx.textAlign = 'center'
  ctx.textBaseline = 'top'
  const secs = WINDOW_MS / 1000
  for (let s = 0; s <= secs; s++) {
    const x = PAD.l + (s / secs) * plotW
    ctx.moveTo(Math.round(x) + 0.5, PAD.t)
    ctx.lineTo(Math.round(x) + 0.5, PAD.t + plotH)
    ctx.fillText(s === secs ? '0 s' : `-${secs - s}`, x, PAD.t + plotH + 5)
  }
  ctx.stroke()

  // Traces
  ctx.save()
  ctx.beginPath()
  ctx.rect(PAD.l, PAD.t, plotW, plotH)
  ctx.clip()
  ctx.lineWidth = 1.75
  ctx.lineJoin = 'round'
  for (let c = 0; c < CHANNELS; c++) {
    if (n === 0) break
    const arr = values[c]
    ctx.beginPath()
    ctx.strokeStyle = COLORS[c]
    for (let i = 0; i < n; i++) {
      const idx = (start + i) % CAPACITY
      const x = PAD.l + ((times[idx] - t0) / WINDOW_MS) * plotW
      const y = PAD.t + plotH - ((arr[idx] - yLo) / ySpan) * plotH
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    }
    ctx.stroke()
  }
  ctx.restore()
}

function resizeCanvas() {
  const container = containerRef.value
  const canvas = canvasRef.value
  if (!container || !canvas) return
  cssW = container.clientWidth
  cssH = container.clientHeight
  dpr = window.devicePixelRatio || 1
  canvas.width = Math.max(1, Math.round(cssW * dpr))
  canvas.height = Math.max(1, Math.round(cssH * dpr))
}

// ---- Vue lifecycle ---------------------------------------------------------------
watch(
  () => props.isRunning,
  (running) => {
    if (running) {
      resetBuffers()
      connect()
    } else {
      disconnect()
    }
  },
)

onMounted(() => {
  resizeCanvas()
  resizeObserver = new ResizeObserver(resizeCanvas)
  if (containerRef.value) resizeObserver.observe(containerRef.value)
  rafId = requestAnimationFrame(draw)
  if (props.isRunning) connect()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  resizeObserver?.disconnect()
  disconnect()
})
</script>

<template>
  <div class="plotter-container" ref="containerRef">
    <canvas ref="canvasRef"></canvas>

    <div class="legend" v-if="isOpen">
      <div class="legend-item"><span class="dot" :style="{ background: COLORS[0] }"></span> Sensor 1</div>
      <div class="legend-item"><span class="dot" :style="{ background: COLORS[1] }"></span> Sensor 2</div>
      <div class="legend-item"><span class="dot" :style="{ background: COLORS[2] }"></span> Sensor 3</div>
    </div>

    <div class="overlay-msg" v-if="!isOpen">
      <p>{{ isRunning ? 'Conectando con el servidor…' : 'La señal se mostrará al iniciar la sesión' }}</p>
    </div>
    <div class="overlay-msg" v-else-if="!hasSignal">
      <p>Conectado, sin datos del sensor. Revisa que el ESP32 esté conectado y la sesión iniciada.</p>
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
  right: 14px;
  display: flex;
  gap: 15px;
  background: rgba(255, 255, 255, 0.85);
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
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 24px;
  background: rgba(248, 250, 252, 0.6);
  color: #64748b;
  font-size: 0.9rem;
  pointer-events: none;
}
</style>
