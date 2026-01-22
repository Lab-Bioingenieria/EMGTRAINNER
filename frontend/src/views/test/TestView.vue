<script setup lang="ts">
import TopHeader from '../../components/common/TopHeader.vue'
import { ref, onMounted, onUnmounted, markRaw } from 'vue'
import { 
    Cpu, Activity, CheckCircle2, AlertTriangle, 
    RefreshCcw, Settings, Terminal, Wifi, WifiOff,
    PlayCircle, StopCircle 
} from 'lucide-vue-next'
import { HealthService } from '../../services/health.service'
import { EmgService } from '../../services/emg.service'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import EmgSerialPlotter from '../../components/common/EmgSerialPlotter.vue'
import { Box3, Vector3 } from 'three'
import type { Group } from 'three'

// 3D Model state
const modelScene = ref<Group | null>(null)
const modelLoading = ref(true)

const systemStatus = ref([
    { name: "MyoArm Band Device", status: "online", ping: "24ms", version: "v2.1.0" },
    { name: "sEMG Signal Processor", status: "online", ping: "12ms", version: "v1.4.2" },
    { name: "WebSocket Server", status: "online", ping: "45ms", version: "v3.0.1" },
    { name: "ML Inference Engine", status: "idle", load: "0%", version: "v2.4.1" },
])

const calibrationSteps = ref([
    { id: 1, name: "Noise Check", status: "completed", log: "Baseline noise < 5uV" },
    { id: 2, name: "MVC Calibration", status: "completed", log: "Max thresholds updated" },
    { id: 3, name: "Crosstalk Analysis", status: "warning", log: "Detecting channel 3 bleed" },
    { id: 4, name: "System Ready", status: "pending", log: "Waiting for check..." },
])

const isRunningTest = ref(false)
const isMonitoring = ref(false)
const WS_URL = "ws://localhost:8000/v1/monitoring/sensor/ws/emg-stream"

const isConnected = ref(false)
const connectionDetails = ref("Buscando dispositivo...")
let healthCheckInterval: number | null = null

const checkConnection = async () => {
    const data = await HealthService.checkPorts()
    if (data.count > 0) {
        isConnected.value = true
        // Assuming the first port is our device for this demo
        const port = data.ports[0]
        connectionDetails.value = `${port.port} - ${port.description}`
    } else {
        isConnected.value = false
        connectionDetails.value = "No se detecta dispositivo conectado"
    }
}

const startTest = async () => {
    isRunningTest.value = true
    try {
        await EmgService.setSessionInfo('System Test')
        await EmgService.startSession('test')
        await EmgService.setMovementLabel('Diagnostics')
        
        setTimeout(async () => {
            await EmgService.stopSession()
            isRunningTest.value = false
        }, 5000)
    } catch (e) {
        console.error("Diagnostic failed", e)
        isRunningTest.value = false
    }
}

// Load 3D model
const loadModel = () => {
    try {
        console.log('🚀 Starting model load...')
        const loader = new GLTFLoader()
        loader.load(
            '/models/ESP32Wroom.glb',
            (gltf) => {
                console.log('✅ Model loaded successfully', gltf)
                
                // Get the scene from GLTF
                const scene = gltf.scene
                
                // Calculate bounding box to center the model
                const box = new Box3().setFromObject(scene)
                const center = new Vector3()
                box.getCenter(center)
                
                // Offset the model so its center is at the origin
                scene.position.x = -center.x
                scene.position.y = -center.y
                scene.position.z = -center.z
                
                // Apply a large scale to make the model visible
                scene.scale.set(50, 50, 50)
                
                console.log('🔧 Model centered and scaled')
                console.log('📦 Center offset:', center)
                
                // Use markRaw to prevent Vue from making the scene reactive
                modelScene.value = markRaw(scene)
                modelLoading.value = false
            },
            (progress) => {
                const percent = (progress.loaded / progress.total) * 100
                console.log('⏳ Loading progress:', percent.toFixed(1), '%')
            },
            (error) => {
                console.error('❌ Error loading model:', error)
                modelLoading.value = false
            }
        )
    } catch (error) {
        console.error('❌ Exception in loadModel:', error)
        modelLoading.value = false
    }
}

onMounted(() => {
    loadModel()
    checkConnection()
    healthCheckInterval = setInterval(checkConnection, 2000) as unknown as number
})

onUnmounted(() => {
    if (healthCheckInterval) clearInterval(healthCheckInterval)
})
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Pruebas de Sistema" subtitle="Diagnóstico de hardware y software" />
    
    <div class="content">
        <div class="container-xl">
             <div class="grid-dashboard">
                 <!-- Status Panel -->
                 <div class="col-main">
                      <div class="card status-card">
                           <div class="card-header">
                                <div>
                                    <h2 class="card-title">Estado de Componentes</h2>
                                    <p class="card-subtitle">Monitoreo en tiempo real de subsistemas</p>
                                </div>
                                <button class="btn btn-primary" @click="startTest" :disabled="isRunningTest">
                                    <RefreshCcw class="icon-sm mr-2" :class="{ 'spin': isRunningTest }" />
                                    {{ isRunningTest ? 'Ejecutando...' : 'Ejecutar Diagnóstico' }}
                                </button>
                           </div>

                           <div class="status-grid">
                                <div v-for="(item, i) in systemStatus" :key="i" class="status-item">
                                     <div class="status-info-group">
                                          <div class="icon-circle" :class="item.status === 'online' ? 'status-online' : 'status-offline'">
                                               <Cpu class="icon-sm" />
                                          </div>
                                          <div class="status-text">
                                              <div class="item-name">{{ item.name }}</div>
                                              <div class="item-version">{{ item.version }}</div>
                                          </div>
                                     </div>
                                     <div class="status-meta">
                                          <span class="badge" :class="item.status === 'online' ? 'badge-success' : 'badge-neutral'">{{ item.status.toUpperCase() }}</span>
                                          <span class="ping-text">{{ item.ping || item.load }}</span>
                                     </div>
                                </div>
                           </div>
                      </div>

                       <div class="card device-view-card">
                           <div class="device-header">
                               <h3 class="device-title">
                                   <Activity class="icon-sm text-blue" /> Vista del Dispositivo
                               </h3>
                               <div class="flex items-center gap-3">
                                   <button 
                                     class="btn-sm" 
                                     :class="isMonitoring ? 'btn-danger' : 'btn-secondary'"
                                     @click="isMonitoring = !isMonitoring"
                                     :disabled="!isConnected"
                                   >
                                       <component :is="isMonitoring ? StopCircle : PlayCircle" class="icon-xs mr-1" />
                                       {{ isMonitoring ? 'Detener Monitor' : 'Monitor en Vivo' }}
                                   </button>
                                   <div class="connection-badge" :class="isConnected ? 'conn-success' : 'conn-error'">
                                       <Wifi v-if="isConnected" class="icon-indicator" />
                                       <WifiOff v-else class="icon-indicator" />
                                       {{ isConnected ? 'CONECTADO' : 'DESCONECTADO' }}
                                   </div>
                               </div>
                           </div>
                           
                           <div class="plotter-section">
                               <EmgSerialPlotter 
                                 :websocket-url="WS_URL" 
                                 :is-running="isMonitoring" 
                                 class="serial-plotter"
                               />
                           </div>
                       </div>
                 </div>

                 <!-- Side Panel -->
                 <div class="col-side">
                      <!-- Calibration Logs -->
                      <div class="card calibration-card">
                           <div class="log-header">
                               <h3 class="log-title">
                                   <Terminal class="icon-sm" /> Logs de Calibración
                               </h3>
                           </div>
                           <div class="log-list">
                                <div v-for="step in calibrationSteps" :key="step.id" class="log-item">
                                     <div class="log-icon-wrapper">
                                          <CheckCircle2 v-if="step.status === 'completed'" class="icon-sm text-green" />
                                          <AlertTriangle v-else-if="step.status === 'warning'" class="icon-sm text-amber" />
                                          <div v-else class="pending-dot"></div>
                                     </div>
                                     <div class="log-content">
                                          <div class="log-name">{{ step.name }}</div>
                                          <div class="log-detail">{{ step.log }}</div>
                                     </div>
                                </div>
                           </div>
                           <div class="log-footer">
                               <button class="link-btn">Ver logs completos</button>
                           </div>
                      </div>

                      <!-- Control Panel -->
                      <div class="card control-card">
                           <h3 class="control-title">
                               <Settings class="icon-sm" /> Configuración Rápida
                           </h3>
                           <div class="control-list">
                                <div class="control-item">
                                     <span class="control-label">Modo Debug</span>
                                     <div class="toggle-switch bg-slate">
                                         <div class="toggle-dot left"></div>
                                     </div>
                                </div>
                                <div class="control-item">
                                     <span class="control-label">Log Verboso</span>
                                     <div class="toggle-switch bg-blue">
                                         <div class="toggle-dot right"></div>
                                     </div>
                                </div>
                           </div>
                      </div>
                 </div>
             </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Layout / Containers */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; }
.container-xl { max-width: 1200px; margin: 0 auto; width: 100%; }

.grid-dashboard { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 1024px) {
    .grid-dashboard { grid-template-columns: 2fr 1fr; }
}

.col-side { display: flex; flex-direction: column; gap: 1.5rem; }

/* Cards */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.status-card { padding: 1.5rem; margin-bottom: 1.5rem; }
.device-view-card { padding: 1.5rem; min-height: 400px; display: flex; flex-direction: column; }
.calibration-card { padding: 0; overflow: hidden; }
.control-card { padding: 1.25rem; }

/* Headers & Titles */
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.card-title { font-size: 1.125rem; font-weight: 700; color: #0f172a; margin: 0; }
.card-subtitle { color: #64748b; font-size: 0.875rem; margin: 0.25rem 0 0 0; }

/* Status Grid */
.status-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; }
@media(min-width: 768px) { .status-grid { grid-template-columns: 1fr 1fr; } }
.status-item { padding: 1rem; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; background-color: #fcfcfc; }
.status-info-group { display: flex; align-items: center; gap: 0.75rem; }
.status-text { display: flex; flex-direction: column; }
.item-name { font-weight: 500; color: #0f172a; font-size: 0.95rem; }
.item-version { font-size: 0.75rem; color: #64748b; font-family: monospace; }
.status-meta { display: flex; align-items: center; gap: 0.75rem; }
.ping-text { font-size: 0.75rem; font-family: monospace; color: #64748b; width: 3rem; text-align: right; }

/* Icons */
.icon-circle { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.status-online { background-color: #dcfce7; color: #16a34a; }
.status-offline { background-color: #f1f5f9; color: #64748b; }
.icon-sm { width: 1.25rem; height: 1.25rem; }
.text-green { color: #22c55e; }
.text-amber { color: #f59e0b; }
.text-blue { color: #2563eb; }

/* Device View */
.device-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; position: relative; z-index: 10; }
.device-title { font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 0.5rem; margin: 0; font-size: 1.1rem; }
.connection-badge { display: flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.conn-success { background-color: #dcfce7; color: #15803d; }
.conn-error { background-color: #fee2e2; color: #b91c1c; }
.icon-indicator { width: 0.75rem; height: 0.75rem; }
.plotter-section { flex: 1; border: 1px solid #f1f5f9; border-radius: 8px; overflow: hidden; background-color: #f8fafc; min-height: 300px; }
.serial-plotter { width: 100%; height: 100%; }

/* Logs Panel */
.log-header { padding: 1rem; border-bottom: 1px solid #f1f5f9; background-color: #f8fafc; }
.log-title { font-weight: 600; color: #0f172a; display: flex; align-items: center; gap: 0.5rem; margin: 0; font-size: 1rem; }
.log-list { display: flex; flex-direction: column; }
.log-item { padding: 1rem; display: flex; gap: 0.75rem; border-bottom: 1px solid #f1f5f9; }
.log-item:last-child { border-bottom: none; }
.log-icon-wrapper { margin-top: 0.25rem; }
.pending-dot { width: 1rem; height: 1rem; border-radius: 50%; border: 2px solid #cbd5e1; box-sizing: border-box; }
.log-content { flex: 1; }
.log-name { font-size: 0.875rem; font-weight: 500; color: #0f172a; }
.log-detail { font-size: 0.75rem; color: #64748b; font-family: monospace; }
.log-footer { padding: 0.75rem; background-color: #f8fafc; text-align: center; border-top: 1px solid #f1f5f9; }
.link-btn { font-size: 0.75rem; color: #2563eb; font-weight: 500; border: none; background: transparent; cursor: pointer; }
.link-btn:hover { text-decoration: underline; }

/* Control Panel */
.control-title { font-weight: 600; color: #0f172a; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; margin-top: 0; font-size: 1rem; }
.control-list { display: flex; flex-direction: column; gap: 0.75rem; }
.control-item { display: flex; align-items: center; justify-content: space-between; }
.control-label { font-size: 0.875rem; color: #334155; }
.toggle-switch { width: 2.5rem; height: 1.5rem; border-radius: 99px; position: relative; cursor: pointer; transition: background 0.2s; }
.toggle-switch.bg-slate { background-color: #e2e8f0; }
.toggle-switch.bg-blue { background-color: #2563eb; }
.toggle-dot { width: 1rem; height: 1rem; background-color: white; border-radius: 50%; position: absolute; top: 0.25rem; box-shadow: 0 1px 2px rgba(0,0,0,0.2); transition: left 0.2s; }
.toggle-dot.left { left: 0.25rem; }
.toggle-dot.right { left: 1.25rem; }

/* Buttons & Badges */
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 500; cursor: pointer; border: none; display: flex; align-items: center; transition: all 0.2s; font-size: 0.9rem; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:hover { background-color: #334155; }
.btn-primary:disabled { opacity: 0.7; cursor: wait; }
.btn-secondary { background-color: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-secondary:hover { background-color: #f8fafc; }
.btn-danger { background-color: #fee2e2; color: #dc2626; border: 1px solid #fecaca; }
.btn-danger:hover { background-color: #fecaca; }
.btn-sm { padding: 0.4rem 0.8rem; font-size: 0.8rem; border-radius: 6px; cursor: pointer; display: flex; align-items: center; font-weight: 500; transition: all 0.2s; }
.badge { font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; }
.badge-success { background-color: #dcfce7; color: #166534; }
.badge-neutral { background-color: #f1f5f9; color: #64748b; }

.mr-2 { margin-right: 0.5rem; }
.mr-1 { margin-right: 0.25rem; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>
