<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { useJointStore } from '@/stores/joint.store'
import type { JointState } from '@/types/joint'

const props = defineProps<{ glb?: string, orbit?: boolean }>()
const container = ref<HTMLDivElement | null>(null)

const jointStore = useJointStore()
const wsConnected = computed(() => jointStore.wsConnected)
const lastMessageTs = computed(() => jointStore.lastMessageTs)
const lastPayload = computed(() => jointStore.lastPayload)
const prettyPayload = computed(() => {
  try {
    const p = lastPayload.value
    if (!p) return '—'
    return JSON.stringify(p, null, 2)
  } catch (e) { return 'parse error' }
})

// expose simple API: playOnceHold, playLoop, restoreSnapshot
function playOnceHold(gesture: string, durationMs: number = 1000) {
  // try to apply preset via joint store
  jointStore.startMock([gesture.toUpperCase()], durationMs)
  setTimeout(() => jointStore.stopMock(), durationMs + 50)
}

function playLoop(gesture: string) {
  jointStore.startMock([gesture.toUpperCase()], 800)
}

function restoreSnapshot() {
  jointStore.stopMock()
}

defineExpose({ playOnceHold, playLoop, restoreSnapshot })

// respond to gesture events from WS via window CustomEvent
function _onGestureEvent(e: any) {
  const d = e.detail
  if (!d || !d.gesture) return
  const gesture = d.gesture
  const mode = d.play_mode || 'once'
  if (mode === 'once') {
    playOnceHold(gesture, 900)
  } else if (mode === 'loop') {
    playLoop(gesture)
  } else {
    playOnceHold(gesture, 900)
  }
}

window.addEventListener('gesture-event', _onGestureEvent as any)

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let raf = 0
let bonesMap = new Map<string, THREE.Object3D>()

function applyJointStateToBones(js: JointState) {
  // Apply joint values (radians) to cached bones; default rotate on X
  for (const [name, angle] of Object.entries(js.joints)) {
    const b = bonesMap.get(name)
    if (!b) continue
    // apply as local rotation around X
    b.rotation.set(angle, 0, 0)
    b.updateMatrixWorld()
  }
}

function animate() {
  const sm = jointStore.smoothed
  if (sm) applyJointStateToBones(sm)
  if (renderer && scene && camera && container.value) {
    renderer.render(scene, camera)
  }
  raf = requestAnimationFrame(animate)
}

onMounted(() => {
  const el = container.value!
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(el.clientWidth, el.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  el.appendChild(renderer.domElement)

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, el.clientWidth / el.clientHeight, 0.1, 1000)
  camera.position.set(0, 1.2, 2.2)

  const light = new THREE.DirectionalLight(0xffffff, 1.0)
  light.position.set(5, 10, 7.5)
  scene.add(light)
  scene.add(new THREE.AmbientLight(0xffffff, 0.6))

  const loader = new GLTFLoader()
  const src = props.glb ?? '/models/dynahand.glb'
  loader.load(src, (gltf) => {
    scene!.add(gltf.scene)

    // cache bones by name (search the scene)
    gltf.scene.traverse((obj) => {
      if (obj.type === 'Bone' || obj.name) {
        bonesMap.set(obj.name, obj)
      }
    })
    // debug: report bones found
    try {
      const names = Array.from(bonesMap.keys())
      console.info('[HandViewer] cached bones:', names.length)
      console.info('[HandViewer] bone sample:', names.slice(0, 50))
    } catch (err) { console.warn('[HandViewer] bones log failed', err) }
  })

  // watch last payload to detect missing bones for incoming JointState payloads
  watch(lastPayload, (nv) => {
    if (!nv) return
    const joints = nv.joints ?? nv.joint_state ?? null
    if (!joints) return
    const missing: string[] = []
    const present: string[] = []
    for (const k of Object.keys(joints)) {
      if (!bonesMap.has(k)) missing.push(k)
      else present.push(k)
    }
    if (missing.length) console.warn('[HandViewer] missing bones for payload:', missing.slice(0,30))
    else console.info('[HandViewer] all payload bones present (sample):', present.slice(0,30))
  }, { immediate: false })

onUnmounted(() => {
  window.removeEventListener('gesture-event', _onGestureEvent as any)
})

  // handle resize
  const onResize = () => {
    if (!renderer || !camera || !el) return
    camera.aspect = el.clientWidth / el.clientHeight
    camera.updateProjectionMatrix()
    renderer.setSize(el.clientWidth, el.clientHeight)
  }
  window.addEventListener('resize', onResize)

  raf = requestAnimationFrame(animate)

  onUnmounted(() => {
    window.removeEventListener('resize', onResize)
    if (raf) cancelAnimationFrame(raf)
    if (renderer) {
      renderer.dispose()
      if (renderer.domElement.parentNode) renderer.domElement.parentNode.removeChild(renderer.domElement)
    }
  })
})
</script>

<template>
  <div style="position:relative; width:100%; height:100%; min-height:300px;">
    <div ref="container" style="width:100%; height:100%;" />

    <div style="position:absolute; right:8px; top:8px; background:rgba(0,0,0,0.6); color:#fff; padding:8px; font-size:12px; border-radius:6px; max-width:240px;">
      <div><strong>WS:</strong> <span :style="{color: wsConnected ? '#8ef' : '#f88'}">{{ wsConnected ? 'connected' : 'disconnected' }}</span></div>
      <div><strong>LastMsg:</strong> {{ lastMessageTs ? new Date(lastMessageTs).toLocaleTimeString() : '—' }}</div>
      <div style="margin-top:6px; font-weight:600">Payload:</div>
      <pre style="max-height:160px; overflow:auto; white-space:pre-wrap; margin:0; font-size:11px;">{{ prettyPayload }}</pre>
    </div>
  </div>
</template>

<style scoped>
.hand-viewer { width: 100%; height: 100%; }
</style>
