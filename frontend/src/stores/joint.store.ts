import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { JointState } from '@/types/joint'

function nowMs() { return performance.now() }

export const useJointStore = defineStore('joint', () => {
  const target = ref<JointState | null>(null)
  const smoothed = ref<JointState | null>(null)
  const playing = ref(false)
  const wsConnected = ref(false)
  const lastMessageTs = ref<number | null>(null)
  const lastPayload = ref<any | null>(null)
  const smoothingMs = ref(120) // time constant for smoothing

  let raf = 0
  let lastTs = nowMs()

  function _ensureSmoothed(init?: JointState) {
    if (!smoothed.value && init) {
      // shallow copy
      smoothed.value = { timestamp: init.timestamp, joints: { ...init.joints } }
    }
  }

  function applyJointState(js: JointState) {
    target.value = js
    _ensureSmoothed(js)
    if (!raf) startLoop()
  }

  function startLoop() {
    lastTs = nowMs()
    const loop = () => {
      const cur = nowMs()
      const dt = Math.max(1, cur - lastTs)
      lastTs = cur

      if (target.value && smoothed.value) {
        const smoothing = (smoothingMs.value ?? 120)
        const alpha = 1 - Math.exp(-dt / smoothing)
        for (const k of Object.keys(target.value.joints)) {
          const t = target.value!.joints[k]
          const s = smoothed.value.joints[k] ?? t
          smoothed.value.joints[k] = s + (t - s) * alpha
        }
        smoothed.value.timestamp = target.value.timestamp
      }

      raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)
  }

  function stopLoop() {
    if (raf) cancelAnimationFrame(raf)
    raf = 0
  }

  // --- Mock generator ---
  let mockInterval: any = null
  const mockRateMs = 60

  const GESTURE_PRESETS: Record<string, JointState> = {
    'OPEN': { timestamp: Date.now() / 1000, joints: { 'thumb_mcp': 0, 'index_mcp': 0, 'index_pip': 0, 'middle_mcp': 0, 'ring_mcp': 0, 'pinky_mcp': 0 } },
    'CLOSE': { timestamp: Date.now() / 1000, joints: { 'thumb_mcp': 1.2, 'index_mcp': 1.0, 'index_pip': 1.0, 'middle_mcp': 1.0, 'ring_mcp': 1.0, 'pinky_mcp': 1.0 } },
    'PINCH': { timestamp: Date.now() / 1000, joints: { 'thumb_mcp': 0.9, 'index_mcp': 0.9, 'index_pip': 0.6 } },
    'POINT': { timestamp: Date.now() / 1000, joints: { 'thumb_mcp': 0.2, 'index_mcp': 0.1, 'index_pip': 0.0, 'middle_mcp': 1.0 } },
  }

  function startMock(sequence: string[] = ['OPEN','CLOSE'], stepMs: number = 1200) {
    stopMock()
    let idx = 0
    playing.value = true
    // emit first immediately
    const emit = () => {
      const name = sequence[idx % sequence.length]
      const preset = GESTURE_PRESETS[name] ?? GESTURE_PRESETS['OPEN']
      applyJointState({ timestamp: Date.now() / 1000, joints: { ...preset.joints } })
      idx++
    }
    emit()
    mockInterval = setInterval(emit, stepMs)
  }

  function stopMock() {
    if (mockInterval) {
      clearInterval(mockInterval)
      mockInterval = null
    }
    playing.value = false
  }

  function setSmoothing(ms: number) { smoothingMs.value = ms }

  // WebSocket client for gestures
  let ws: WebSocket | null = null
  const reconnectMs = 1500

  function _dispatchGestureEvent(payload: any) {
    try {
      const ev = new CustomEvent('gesture-event', { detail: payload })
      window.dispatchEvent(ev)
    } catch (e) { }
  }

  async function connectWsGesture(url: string) {
    try {
      if (ws) ws.close()
      ws = new WebSocket(url)
      ws.onopen = () => { wsConnected.value = true }
      ws.onmessage = (m) => {
        try {
          const obj = JSON.parse(m.data)
          lastMessageTs.value = Date.now()
          lastPayload.value = obj
          _dispatchGestureEvent(obj)
        } catch (e) {
          console.warn('ws gesture parse', e)
        }
      }
      ws.onclose = () => { wsConnected.value = false; ws = null; setTimeout(() => connectWsGesture(url), reconnectMs) }
      ws.onerror = () => { wsConnected.value = false }
    } catch (e) {
      wsConnected.value = false
      // fallback to mock
      startMock()
    }
  }

  function disconnectWsGesture() {
    if (ws) {
      try { ws.close() } catch(e) {}
      ws = null
    }
    wsConnected.value = false
  }

  return { target, smoothed, playing, wsConnected, lastMessageTs, lastPayload, applyJointState, startMock, stopMock, setSmoothing, connectWsGesture, disconnectWsGesture }
})
