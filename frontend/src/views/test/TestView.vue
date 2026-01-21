<script setup lang="ts">
import TopHeader from '../../components/common/TopHeader.vue'
import { ref, onMounted, onUnmounted, shallowRef, markRaw } from 'vue'
import { 
    Cpu, Activity, Zap, CheckCircle2, AlertTriangle, 
    RefreshCcw, Settings, Terminal, Wifi, WifiOff
} from 'lucide-vue-next'
import { TresCanvas } from '@tresjs/core'
import { OrbitControls, ContactShadows } from '@tresjs/cientos'
import { HealthService } from '../../services/health.service'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
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

const startTest = () => {
    isRunningTest.value = true
    setTimeout(() => isRunningTest.value = false, 2000)
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
             <div class="grid-dashboard gap-6">
                 <!-- Status Panel -->
                 <div class="col-main">
                      <div class="card p-6 mb-6">
                           <div class="flex-row-between mb-6">
                                <div>
                                    <h2 class="text-lg font-bold text-slate-900">Estado de Componentes</h2>
                                    <p class="text-slate-500 text-sm">Monitoreo en tiempo real de subsistemas</p>
                                </div>
                                <button class="btn btn-primary" @click="startTest" :disabled="isRunningTest">
                                    <RefreshCcw class="icon-sm mr-2" :class="{ 'spin': isRunningTest }" />
                                    {{ isRunningTest ? 'Ejecutando...' : 'Ejecutar Diagnóstico' }}
                                </button>
                           </div>

                           <div class="status-grid">
                                <div v-for="(item, i) in systemStatus" :key="i" class="status-item">
                                     <div class="flex items-center gap-3">
                                          <div class="icon-circle" :class="item.status === 'online' ? 'bg-green-100 text-green-600' : 'bg-slate-100 text-slate-500'">
                                               <Cpu class="icon-sm" />
                                          </div>
                                          <div>
                                              <div class="font-medium text-slate-900">{{ item.name }}</div>
                                              <div class="text-xs text-muted font-mono">{{ item.version }}</div>
                                          </div>
                                     </div>
                                     <div class="flex items-center gap-3">
                                          <span class="badge" :class="item.status === 'online' ? 'badge-success' : 'badge-neutral'">{{ item.status.toUpperCase() }}</span>
                                          <span class="text-xs font-mono text-muted w-12 text-right">{{ item.ping || item.load }}</span>
                                     </div>
                                </div>
                           </div>
                      </div>

                       <div class="card p-6 relative overflow-hidden">
                           <div class="flex items-center justify-between mb-4 z-10 relative">
                               <h3 class="font-bold text-slate-900 flex items-center gap-2">
                                   <Activity class="icon-sm text-blue-600" /> Vista del Dispositivo
                               </h3>
                               <div class="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold"
                                    :class="isConnected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                                   <Wifi v-if="isConnected" class="w-3 h-3" />
                                   <WifiOff v-else class="w-3 h-3" />
                                   {{ isConnected ? 'CONECTADO' : 'DESCONECTADO' }}
                               </div>
                           </div>
                           <!-- Model Viewer 
                            <div class="model-viewer-container">
                                <TresCanvas class="tres-canvas-fixed">
                                    <TresPerspectiveCamera :position="[2, 2, 2]" :fov="60" />
                                    <OrbitControls :enable-damping="true" :auto-rotate="true" :auto-rotate-speed="1" />
                                    
                                    <TresAmbientLight :intensity="3" />
                                    <TresDirectionalLight :position="[5, 5, 5]" :intensity="2" />
                                    <TresDirectionalLight :position="[-5, 5, -5]" :intensity="1.5" />
                                    <TresDirectionalLight :position="[0, 10, 0]" :intensity="1" />
                                    
                                    <primitive v-if="modelScene" :object="modelScene" />
                                    <TresMesh v-else :position="[0, 0, 0]">
                                        <TresBoxGeometry :args="[1, 1, 1]" />
                                        <TresMeshStandardMaterial color="#3b82f6" />
                                    </TresMesh>
                                    
                                    <TresGridHelper :args="[10, 10]" />
                                    <ContactShadows :opacity="0.3" :blur="2" />
                                </TresCanvas>
                                
                                <div class="status-overlay">
                                    <div class="text-xs font-mono text-slate-500 mb-1">STATUS DEL PUERTO</div>
                                    <div class="font-semibold text-slate-800 text-sm truncate">{{ connectionDetails }}</div>
                                </div>
                           </div>-->
                       </div>
                 </div>

                 <!-- Side Panel -->
                 <div class="col-side flex flex-col gap-6">
                      <!-- Calibration Logs -->
                      <div class="card p-0 overflow-hidden">
                           <div class="p-4 border-b border-slate-100 bg-slate-50/50">
                               <h3 class="font-semibold text-slate-900 flex items-center gap-2">
                                   <Terminal class="icon-sm" /> Logs de Calibración
                               </h3>
                           </div>
                           <div class="divide-y divide-slate-100">
                                <div v-for="step in calibrationSteps" :key="step.id" class="p-4 flex gap-3">
                                     <div class="mt-1">
                                          <CheckCircle2 v-if="step.status === 'completed'" class="icon-sm text-green-500" />
                                          <AlertTriangle v-else-if="step.status === 'warning'" class="icon-sm text-amber-500" />
                                          <div v-else class="w-4 h-4 rounded-full border-2 border-slate-300"></div>
                                     </div>
                                     <div class="flex-1">
                                          <div class="text-sm font-medium text-slate-900">{{ step.name }}</div>
                                          <div class="text-xs text-slate-500 font-mono">{{ step.log }}</div>
                                     </div>
                                </div>
                           </div>
                           <div class="p-3 bg-slate-50 text-center border-t border-slate-100">
                               <button class="text-xs text-blue-600 font-medium hover:underline">Ver logs completos</button>
                           </div>
                      </div>

                      <!-- Control Panel -->
                      <div class="card p-5">
                           <h3 class="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                               <Settings class="icon-sm" /> Configuración Rápida
                           </h3>
                           <div class="space-y-3">
                                <div class="flex items-center justify-between">
                                     <span class="text-sm text-slate-700">Modo Debug</span>
                                     <div class="toggle bg-slate-200 w-10 h-6 rounded-full relative cursor-pointer">
                                         <div class="dot bg-white w-4 h-4 rounded-full absolute top-1 left-1 shadow-sm"></div>
                                     </div>
                                </div>
                                <div class="flex items-center justify-between">
                                     <span class="text-sm text-slate-700">Log Verboso</span>
                                     <div class="toggle bg-blue-600 w-10 h-6 rounded-full relative cursor-pointer">
                                         <div class="dot bg-white w-4 h-4 rounded-full absolute top-1 right-1 shadow-sm"></div>
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
/* Standard Layout */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; }
.container-xl { max-width: 1200px; margin: 0 auto; width: 100%; }

.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.grid-dashboard { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 1024px) {
    .grid-dashboard { grid-template-columns: 2fr 1fr; }
}

.status-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; }
@media(min-width: 768px) { .status-grid { grid-template-columns: 1fr 1fr; } }

.status-item { padding: 1rem; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; background-color: #fcfcfc; }

/* Components */
.icon-circle { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.bg-green-100 { background-color: #dcfce7; }
.text-green-600 { color: #16a34a; }
.text-green-500 { color: #22c55e; }
.text-amber-500 { color: #f59e0b; }
.icon-sm { width: 1.25rem; height: 1.25rem; }
.spin { animation: spin 1s linear infinite; }

.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 500; font-size: 0.9rem; cursor: pointer; border: none; display: flex; align-items: center; transition: all 0.2s; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:disabled { opacity: 0.7; cursor: wait; }

.badge { font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; }
.badge-success { background-color: #dcfce7; color: #166534; }
.badge-neutral { background-color: #f1f5f9; color: #64748b; }

.flex-row-between { display: flex; justify-content: space-between; align-items: center; }
.flex-center { display: flex; justify-content: center; align-items: center; }
.flex-col { flex-direction: column; }
.mr-2 { margin-right: 0.5rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mt-1 { margin-top: 0.25rem; }

/* 3D Model Viewer Styles */
.model-viewer-container {
    position: relative;
    width: 100%;
    height: 16rem; /* 256px - h-64 equivalent */
    background-color: #0f172a;
    border-radius: 0.75rem;
    border: 1px solid #e2e8f0;
    overflow: hidden;
}

.tres-canvas-fixed {
    width: 100% !important;
    height: 100% !important;
    display: block;
}

.status-overlay {
    position: absolute;
    bottom: 1rem;
    left: 1rem;
    right: 1rem;
    background-color: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(8px);
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.model-viewer-container:hover .status-overlay {
    bottom: 1rem;
}

@keyframes spin { 100% { transform: rotate(360deg); } }
</style>
