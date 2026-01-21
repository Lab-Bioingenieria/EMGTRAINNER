<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import DoctorEMGChart from '../../components/doctor/DoctorEMGChart.vue'
import DoctorGestureMonitor from '../../components/doctor/DoctorGestureMonitor.vue'
import DoctorAlerts from '../../components/doctor/DoctorAlerts.vue'
import {
  Activity, RotateCcw, Check, Copy, Wifi, WifiOff, AlertTriangle,
  Play, Pause, Square, Plus
} from 'lucide-vue-next'
import { useSessionStore } from '../../stores/session'
import { ALL_GESTURES } from '../../lib/constants'
import type { TrainingMode, Gesture } from '../../lib/constants'

// Store
const store = useSessionStore()

// Local State
const codeCopied = ref(false)
const tempSelectedGestures = ref<Gesture[]>([])
const protocolName = ref("")
const repetitions = ref(3)
const restTime = ref(5)
const generateCode = ref(true)

// Computed Helpers
const formattedTime = computed(() => {
  const seconds = store.sessionTime
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
})

const activeSignals = computed(() => store.emgSignals.filter(s => s.status === 'active').length)
const canStartSession = computed(() => activeSignals.value >= 3)
const phase = computed(() => store.phase)
const trainingMode = computed(() => store.trainingMode)

// Methods
const copyCode = () => {
    navigator.clipboard.writeText(store.sessionCode)
    codeCopied.value = true
    setTimeout(() => codeCopied.value = false, 2000)
}

const handleSelectMode = (mode: TrainingMode) => {
    store.setTrainingMode(mode)
    if (mode === "LLC") {
        // Random Selection
        const shuffled = [...ALL_GESTURES].sort(() => Math.random() - 0.5)
        store.setSelectedGestures(shuffled)
    }
}

const toggleGesture = (gesture: Gesture) => {
    const exists = tempSelectedGestures.value.find(g => g.id === gesture.id)
    if (exists) {
        tempSelectedGestures.value = tempSelectedGestures.value.filter(g => g.id !== gesture.id)
    } else {
        tempSelectedGestures.value.push(gesture)
    }
}

const handleConfirmGestures = () => {
    store.setSelectedGestures(tempSelectedGestures.value)
}

const handleStartWaiting = () => {
    if (generateCode.value) {
        store.generateNewCode()
    }
    store.setPhase('waiting')
}

// Timer Logic
let interval: number | null = null

onMounted(() => {
    interval = window.setInterval(() => {
        if (store.phase === 'running') {
            store.incrementTime()
        }
    }, 1000)
})

// Simulate Patient Connection Side-effect
watch(phase, (newPhase) => {
    if (newPhase === 'waiting') {
        setTimeout(() => {
            if (store.phase === 'waiting') {
                store.setPhase('connected')
            }
        }, 3000)
    }
})

onUnmounted(() => {
    if (interval) clearInterval(interval)
})
</script>

<template>
  <div class="page-layout">
    <!-- PHASE: Setup (No Mode) -->
    <template v-if="phase === 'setup' && !trainingMode">
        <TopHeader title="Sesión Doctor" subtitle="Configurar protocolo de entrenamiento" />
        <div class="content">
            <div class="setup-container">
                <!-- Protocol Name -->
                <div class="card bg-white mb-section">
                    <h3 class="card-title mb-input">Nuevo Protocolo</h3>
                    <div class="field-group">
                        <label>Nombre del protocolo (opcional)</label>
                        <input v-model="protocolName" placeholder="Ej: Rehabilitación inicial..." class="input" />
                    </div>
                </div>

                <h2 class="section-title">Seleccionar Modo de Entrenamiento</h2>
                <div class="grid-modes">
                    <!-- TLC -->
                    <div class="mode-card" @click="handleSelectMode('TLC')">
                         <div class="mode-header">
                             <div class="icon-circle"><Activity class="icon text-primary" /></div>
                             <div>
                                 <h3 class="mode-title">Modo Guiado (TLC)</h3>
                                 <p class="mode-subtitle">Teacher-Led Control</p>
                             </div>
                         </div>
                         <p class="mode-desc">Usted define los gestos, repeticiones y tiempos. Ideal para sesiones supervisadas.</p>
                    </div>
                    <!-- LLC -->
                    <div class="mode-card" @click="handleSelectMode('LLC')">
                         <div class="mode-header">
                             <div class="icon-circle"><RotateCcw class="icon text-primary" /></div>
                             <div>
                                 <h3 class="mode-title">Modo Autónomo (LLC)</h3>
                                 <p class="mode-subtitle">Learner-Led Control</p>
                             </div>
                         </div>
                         <p class="mode-desc">El sistema presenta gestos de forma adaptativa. El paciente controla el flujo.</p>
                    </div>
                </div>
            </div>
        </div>
    </template>

    <!-- PHASE: Setup TLC Gestures -->
    <template v-else-if="phase === 'setup' && trainingMode === 'TLC' && store.selectedGestures.length === 0">
         <TopHeader title="Sesión Doctor" subtitle="Modo Guiado (TLC) - Configurar protocolo" />
         <div class="content">
             <div class="setup-container">
                 <div class="section-header">
                    <h2 class="section-title">Gestos del Protocolo</h2>
                    <span class="count-badge">{{ tempSelectedGestures.length }} seleccionados</span>
                 </div>

                 <div class="grid-gestures mb-section">
                    <div v-for="gesture in ALL_GESTURES" :key="gesture.id"
                         class="gesture-item"
                         :class="{ selected: tempSelectedGestures.find(g => g.id === gesture.id) }"
                         @click="toggleGesture(gesture)"
                    >
                        <h3 class="gesture-name">{{ gesture.name }}</h3>
                        <p class="gesture-sub">{{ gesture.nameEn }}</p>
                    </div>
                 </div>

                 <div class="card bg-white mb-section">
                     <h3 class="card-title mb-input">Parámetros</h3>
                     <div class="grid-params">
                         <div class="field-group">
                             <label>Repeticiones por gesto</label>
                             <input type="number" v-model.number="repetitions" min="1" max="10" class="input" />
                         </div>
                         <div class="field-group">
                             <label>Tiempo de descanso (seg)</label>
                             <input type="number" v-model.number="restTime" min="1" max="30" class="input" />
                         </div>
                     </div>
                 </div>

                 <div class="action-buttons">
                     <button class="btn btn-ghost" @click="store.setTrainingMode(null)">Cambiar modo</button>
                     <button class="btn btn-primary" :disabled="tempSelectedGestures.length === 0" @click="handleConfirmGestures">
                         Confirmar Protocolo
                     </button>
                 </div>
             </div>
         </div>
    </template>

    <!-- PHASE: Setup Verification -->
    <template v-else-if="phase === 'setup' && store.selectedGestures.length > 0">
        <TopHeader title="Sesión Doctor" subtitle="Verificar señales sEMG" />
        <div class="content">
            <div class="setup-container">
                 <div class="card info-bar mb-section">
                      <div class="info-left">
                          <span class="badge info-badge">{{ trainingMode === 'TLC' ? 'Modo Guiado' : 'Modo Autónomo' }}</span>
                          <span class="info-text">{{ store.selectedGestures.length }} gestos</span>
                      </div>
                      <div class="code-section" v-if="generateCode">
                          <code class="session-code">{{ store.sessionCode }}</code>
                          <button class="btn-icon" @click="copyCode">
                              <Check v-if="codeCopied" class="icon-sm text-success" />
                              <Copy v-else class="icon-sm" />
                          </button>
                      </div>
                 </div>

                 <div class="card signals-card mb-section">
                      <div class="signals-header">
                          <h3 class="card-title">Estado de Señales sEMG</h3>
                          <span class="status-badge" :class="canStartSession ? 'bg-success' : 'bg-destructive'">
                               <Wifi v-if="canStartSession" class="icon-xs mr-1" />
                               <WifiOff v-else class="icon-xs mr-1" />
                               {{ activeSignals }}/3 Activas
                          </span>
                      </div>
                      <div class="signals-grid">
                          <div v-for="signal in store.emgSignals" :key="signal.id" 
                               class="signal-item" :class="signal.status">
                               <div class="signal-dot"></div>
                               <p class="signal-name">{{ signal.name }}</p>
                          </div>
                      </div>
                      <div v-if="!canStartSession" class="alert-message">
                          <AlertTriangle class="icon-sm text-destructive" />
                          <span>Se requieren 3 señales activas.</span>
                      </div>
                 </div>

                 <div class="action-buttons">
                     <button class="btn btn-ghost" @click="trainingMode === 'TLC' ? store.setSelectedGestures([]) : store.setTrainingMode(null)">
                         Editar
                     </button>
                     <button class="btn btn-primary" :disabled="!canStartSession" @click="handleStartWaiting">
                         {{ generateCode ? 'Iniciar y Esperar' : 'Iniciar Sesión' }}
                     </button>
                 </div>
            </div>
        </div>
    </template>

    <!-- PHASE: Waiting -->
    <template v-else-if="phase === 'waiting'">
        <TopHeader title="Sesión Doctor" subtitle="Esperando conexión..." />
        <div class="content layout-center">
             <div class="waiting-card">
                 <div class="pulse-icon"><Wifi class="icon-lg text-primary" /></div>
                 <h2 class="waiting-title">Esperando Conexión</h2>
                 <p class="waiting-subtitle">Comparta el código con el paciente.</p>
                 <div class="code-wrapper">
                      <code class="code-big">{{ store.sessionCode }}</code>
                 </div>
                 <button class="btn btn-outline" @click="store.resetSession">Cancelar</button>
             </div>
        </div>
    </template>

    <!-- PHASE: Running / Connected / Paused / Finished -->
    <template v-else>
         <TopHeader 
            title="Sesión Doctor" 
            :subtitle="phase === 'connected' ? 'Paciente conectado' : phase === 'running' ? 'En curso' : 'Estado: ' + phase" 
         />
         <div class="content">
             <div class="dashboard-container">
                  <!-- Control Bar -->
                  <div class="control-bar mb-section">
                       <div class="status-group">
                           <span class="status-label" :class="'status-' + phase">{{ phase }}</span>
                           <span class="timer-display">{{ formattedTime }}</span>
                       </div>
                       <div class="controls-group">
                           <button v-if="phase === 'connected'" class="btn btn-success" @click="store.setPhase('running')">
                               <Play class="icon-sm mr-2" /> Iniciar
                           </button>
                           <template v-if="phase === 'running'">
                               <button class="btn btn-outline" @click="store.setPhase('paused')"><Pause class="icon-sm mr-2"/> Pausar</button>
                               <button class="btn btn-destructive" @click="store.setPhase('finished')"><Square class="icon-sm mr-2"/> Finalizar</button>
                           </template>
                           <template v-if="phase === 'paused'">
                               <button class="btn btn-success" @click="store.setPhase('running')"><Play class="icon-sm mr-2"/> Continuar</button>
                               <button class="btn btn-destructive" @click="store.setPhase('finished')"><Square class="icon-sm mr-2"/> Finalizar</button>
                           </template>
                           <button v-if="phase === 'finished'" class="btn btn-primary" @click="store.resetSession">
                               <Plus class="icon-sm mr-2" /> Nueva Sesión
                           </button>
                       </div>
                  </div>

                  <div class="dashboard-grid">
                      <div class="chart-area">
                          <DoctorEMGChart :is-running="phase === 'running'" />
                      </div>
                      <div class="widgets-area">
                          <DoctorGestureMonitor gesture="Cerrar Mano" />
                          <DoctorAlerts />
                      </div>
                  </div>
             </div>
         </div>
    </template>
  </div>
</template>

<style scoped>
/* Base Layout */
.page-layout { display: flex; flex-direction: column; height: 100%; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 1.5rem; }
.setup-container { max-width: 56rem; margin: 0 auto; width: 100%; }
.dashboard-container { max-width: 80rem; margin: 0 auto; width: 100%; }
.layout-center { display: flex; align-items: center; justify-content: center; }

/* Cards & Containers */
.card { background: white; border-radius: 8px; border: 1px solid #e2e8f0; padding: 1.5rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.bg-white { background-color: white; }
.mb-section { margin-bottom: 1.5rem; }
.mb-input { margin-bottom: 1rem; }

/* Typography */
.card-title { font-size: 1rem; font-weight: 600; color: #0f172a; margin: 0; }
.section-title { font-size: 1.125rem; font-weight: 600; color: #0f172a; margin-bottom: 1rem; }

/* Forms */
.field-group { display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.875rem; color: #475569; font-weight: 500; }
.input { padding: 0.625rem; border: 1px solid #e2e8f0; border-radius: 6px; width: 100%; font-size: 0.9rem; box-sizing: border-box; }
.input:focus { border-color: #3b82f6; outline: none; }

/* Mode Selection */
.grid-modes { display: grid; grid-template-columns: 1fr; gap: 1rem; }
@media (min-width: 768px) { .grid-modes { grid-template-columns: 1fr 1fr; } }

.mode-card { 
    background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; cursor: pointer; transition: all 0.2s; 
}
.mode-card:hover { border-color: #3b82f6; background-color: #f8fafc; transform: translateY(-2px); }
.mode-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem; }
.icon-circle { width: 40px; height: 40px; border-radius: 50%; background-color: #eff6ff; display: flex; align-items: center; justify-content: center; }
.mode-title { font-weight: 600; font-size: 1rem; color: #0f172a; margin: 0; }
.mode-subtitle { font-size: 0.75rem; color: #64748b; margin: 0; }
.mode-desc { font-size: 0.875rem; color: #64748b; line-height: 1.5; }

/* Gestures Grid */
.grid-gestures { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
@media(min-width: 768px) { .grid-gestures { grid-template-columns: repeat(4, 1fr); } }

.gesture-item { 
    background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.2s;
}
.gesture-item:hover { background-color: #f8fafc; }
.gesture-item.selected { border-color: #3b82f6; background-color: #eff6ff; }
.gesture-name { font-size: 0.875rem; font-weight: 500; color: #0f172a; margin: 0; }
.gesture-sub { font-size: 0.75rem; color: #64748b; margin: 0; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.count-badge { background-color: #f1f5f9; color: #64748b; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 500; }

/* Params Grid */
.grid-params { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 768px) { .grid-params { grid-template-columns: 1fr 1fr; } }

/* Verification Bar */
.info-bar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; }
.info-left { display: flex; align-items: center; gap: 1rem; }
.info-badge { background-color: #eff6ff; color: #1d4ed8; padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.875rem; font-weight: 500; }
.info-text { color: #64748b; font-size: 0.875rem; }
.code-section { display: flex; align-items: center; gap: 0.5rem; }
.session-code { font-family: monospace; font-weight: 700; background: #f1f5f9; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 1rem; }

/* Signals Card */
.signals-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.status-badge { display: flex; align-items: center; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.bg-success { background-color: #dcfce7; color: #166534; }
.bg-destructive { background-color: #fee2e2; color: #991b1b; }

.signals-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; }
.signal-item { padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; background-color: #f8fafc; }
.signal-item.active { border-color: #bbf7d0; background-color: #f0fdf4; }
.signal-dot { width: 10px; height: 10px; border-radius: 50%; background-color: #cbd5e1; margin: 0 auto 0.5rem; }
.signal-item.active .signal-dot { background-color: #22c55e; }
.signal-name { font-weight: 500; font-size: 0.875rem; }

.alert-message { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background-color: #fee2e2; border-radius: 6px; color: #991b1b; font-size: 0.875rem; margin-top: 1rem; }

/* Waiting Screen */
.waiting-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 3rem; text-align: center; max-width: 28rem; width: 100%; }
.pulse-icon { width: 64px; height: 64px; background-color: #eff6ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; animation: pulse 2s infinite; }
.waiting-title { font-size: 1.25rem; font-weight: 600; color: #0f172a; margin-bottom: 0.5rem; }
.waiting-subtitle { color: #64748b; margin-bottom: 1.5rem; }
.code-wrapper { margin-bottom: 1.5rem; }
.code-big { font-family: monospace; font-size: 2rem; letter-spacing: 0.1em; background: #f1f5f9; padding: 0.5rem 1.5rem; border-radius: 8px; font-weight: 700; color: #0f172a; }

/* Dashboard Running */
.control-bar { background: white; border-radius: 8px; border: 1px solid #e2e8f0; padding: 0.75rem 1.5rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.status-group { display: flex; align-items: center; gap: 1rem; }
.status-label { text-transform: capitalize; padding: 0.25rem 0.75rem; border-radius: 4px; font-weight: 600; font-size: 0.875rem; }
.status-running { background-color: #dcfce7; color: #166534; }
.status-paused { background-color: #fef3c7; color: #92400e; }
.status-finished { background-color: #dbeafe; color: #1e40af; }
.status-connected { background-color: #f3e8ff; color: #6b21a8; }
.timer-display { font-family: monospace; font-size: 1.125rem; font-weight: 600; color: #0f172a; }
.controls-group { display: flex; gap: 0.5rem; }

.dashboard-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 1024px) {
    .dashboard-grid { grid-template-columns: 2fr 1fr; }
}
.side-widgets { display: flex; flex-direction: column; gap: 1.5rem; }

/* Buttons & Common */
.action-buttons { display: flex; gap: 0.75rem; }
.btn { padding: 0.5rem 1rem; border-radius: 6px; font-weight: 500; font-size: 0.875rem; cursor: pointer; border: none; transition: background 0.2s; display: inline-flex; align-items: center; justify-content: center; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:hover { background-color: #1e293b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-ghost { background: transparent; color: #0f172a; }
.btn-ghost:hover { background-color: #f1f5f9; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-success { background-color: #16a34a; color: white; }
.btn-destructive { background-color: #dc2626; color: white; }
.btn-icon { padding: 0.5rem; border-radius: 6px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: flex; align-items: center; justify-content: center; }

/* Icons */
.icon { width: 1.25rem; height: 1.25rem; }
.icon-sm { width: 1rem; height: 1rem; }
.icon-xs { width: 0.75rem; height: 0.75rem; }
.icon-lg { width: 2rem; height: 2rem; }
.text-primary { color: #2563eb; }
.text-success { color: #16a34a; }
.text-destructive { color: #dc2626; }
.mr-1 { margin-right: 0.25rem; }
.mr-2 { margin-right: 0.5rem; }

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
    70% { box-shadow: 0 0 0 20px rgba(59, 130, 246, 0); }
    100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}
</style>
