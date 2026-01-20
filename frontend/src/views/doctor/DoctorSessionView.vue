<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
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
        // Simulate patient connection
        if (store.phase === 'waiting') {
            // In a real app this would be a socket event
            // Using a simple check to simulate "after 3 seconds connected"
            // For now we will manually trigger connection or just simulate with setTimeout logic
            // inside the check-interval is risky, let's do a standalone timeout
        }
    }, 1000)
})

// Simulate Patient Connection Side-effect
// We'll use a watcher on phase in a real scenario, but here simple timeout:
import { watch } from 'vue'
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
            <div class="max-w-4xl mx-auto">
                <!-- Protocol Name -->
                <div class="card mb-6">
                    <h3 class="card-title mb-4">Nuevo Protocolo</h3>
                    <div class="field-group">
                        <label>Nombre del protocolo (opcional)</label>
                        <input v-model="protocolName" placeholder="Ej: Rehabilitación inicial..." class="input" />
                    </div>
                </div>

                <h2 class="section-title">Seleccionar Modo de Entrenamiento</h2>
                <div class="grid-2">
                    <!-- TLC -->
                    <div class="card hoverable-card" @click="handleSelectMode('TLC')">
                         <div class="card-head-row">
                             <div class="icon-bubble"><Activity class="icon text-primary" /></div>
                             <div>
                                 <h3 class="font-medium">Modo Guiado (TLC)</h3>
                                 <p class="text-xs text-muted">Teacher-Led Control</p>
                             </div>
                         </div>
                         <p class="desc-text">Usted define los gestos, repeticiones y tiempos. Ideal para sesiones supervisadas.</p>
                    </div>
                    <!-- LLC -->
                    <div class="card hoverable-card" @click="handleSelectMode('LLC')">
                         <div class="card-head-row">
                             <div class="icon-bubble"><RotateCcw class="icon text-primary" /></div>
                             <div>
                                 <h3 class="font-medium">Modo Autónomo (LLC)</h3>
                                 <p class="text-xs text-muted">Learner-Led Control</p>
                             </div>
                         </div>
                         <p class="desc-text">El sistema presenta gestos de forma adaptativa. El paciente controla el flujo.</p>
                    </div>
                </div>
            </div>
        </div>
    </template>

    <!-- PHASE: Setup TLC Gestures -->
    <template v-else-if="phase === 'setup' && trainingMode === 'TLC' && store.selectedGestures.length === 0">
         <TopHeader title="Sesión Doctor" subtitle="Modo Guiado (TLC) - Configurar protocolo" />
         <div class="content">
             <div class="max-w-4xl mx-auto">
                 <div class="flex items-center justify-between mb-4">
                    <h2 class="section-title">Gestos del Protocolo</h2>
                    <span class="badge">{{ tempSelectedGestures.length }} seleccionados</span>
                 </div>

                 <div class="grid-gestures mb-6">
                    <div v-for="gesture in ALL_GESTURES" :key="gesture.id"
                         class="card gesture-card"
                         :class="{ selected: tempSelectedGestures.find(g => g.id === gesture.id) }"
                         @click="toggleGesture(gesture)"
                    >
                        <h3 class="text-sm font-medium">{{ gesture.name }}</h3>
                        <p class="text-xs text-muted">{{ gesture.nameEn }}</p>
                    </div>
                 </div>

                 <div class="card mb-6">
                     <h3 class="card-title mb-4">Parámetros</h3>
                     <div class="grid-2 gap-6">
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

                 <div class="flex gap-3">
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
            <div class="max-w-4xl mx-auto">
                 <div class="card mb-6 flex-row-between">
                      <div class="flex items-center gap-3">
                          <span class="badge badge-primary">{{ trainingMode === 'TLC' ? 'Modo Guiado' : 'Modo Autónomo' }}</span>
                          <span class="text-sm text-muted">{{ store.selectedGestures.length }} gestos</span>
                      </div>
                      <div class="flex items-center gap-2" v-if="generateCode">
                          <code class="code-block">{{ store.sessionCode }}</code>
                          <button class="btn-icon" @click="copyCode">
                              <Check v-if="codeCopied" class="icon-sm text-success" />
                              <Copy v-else class="icon-sm" />
                          </button>
                      </div>
                 </div>

                 <div class="card mb-6">
                      <div class="card-head-row space-between">
                          <h3 class="card-title">Estado de Señales sEMG</h3>
                          <span class="badge badge-signals" :class="canStartSession ? 'bg-success' : 'bg-destructive'">
                               <Wifi v-if="canStartSession" class="icon-xs mr-1" />
                               <WifiOff v-else class="icon-xs mr-1" />
                               {{ activeSignals }}/3 Activas
                          </span>
                      </div>
                      <div class="grid-3 gap-4 mt-4">
                          <div v-for="signal in store.emgSignals" :key="signal.id" 
                               class="signal-box" :class="signal.status">
                               <div class="status-dot"></div>
                               <p class="font-medium">{{ signal.name }}</p>
                          </div>
                      </div>
                      <div v-if="!canStartSession" class="alert-box mt-4">
                          <AlertTriangle class="icon-sm text-destructive" />
                          <span>Se requieren 3 señales activas.</span>
                      </div>
                 </div>

                 <div class="flex gap-3">
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
        <div class="content flex-center">
             <div class="card max-w-md w-full text-center py-8">
                 <div class="pulse-ring mx-auto mb-6"><Wifi class="icon-lg text-primary" /></div>
                 <h2 class="text-xl font-medium mb-2">Esperando Conexión</h2>
                 <p class="text-muted mb-6">Comparta el código con el paciente.</p>
                 <div class="flex-center gap-2 mb-6">
                      <code class="code-display">{{ store.sessionCode }}</code>
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
             <div class="max-w-7xl mx-auto">
                  <!-- Control Bar -->
                  <div class="card mb-6 py-3 flex-row-between">
                       <div class="flex items-center gap-4">
                           <span class="badge capitalize" :class="'badge-' + phase">{{ phase }}</span>
                           <span class="font-mono text-lg">{{ formattedTime }}</span>
                       </div>
                       <div class="flex gap-2">
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

                  <div class="grid-dashboard gap-6">
                      <div class="main-chart">
                          <DoctorEMGChart :is-running="phase === 'running'" />
                      </div>
                      <div class="side-widgets">
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
/* Reuse layout base */
.page-layout { display: flex; flex-direction: column; height: 100%; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 1.5rem; }
.card { background: white; border-radius: 8px; border: 1px solid #e2e8f0; padding: 1.5rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

/* Typography */
.card-title { font-size: 1rem; font-weight: 600; color: #0f172a; margin: 0; }
.section-title { font-size: 1.1rem; font-weight: 500; margin-bottom: 1rem; color: #0f172a; }
.text-muted { color: #64748b; }

/* Grid Layouts */
.max-w-4xl { max-width: 56rem; }
.max-w-7xl { max-width: 80rem; }
.grid-2 { display: grid; grid-template-columns: 1fr; gap: 1rem; }
@media (min-width: 768px) { .grid-2 { grid-template-columns: 1fr 1fr; } }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); }
.grid-gestures { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
@media(min-width: 768px) { .grid-gestures { grid-template-columns: repeat(4, 1fr); } }

/* Cards & Interactions */
.hoverable-card { cursor: pointer; transition: all 0.2s; border: 1px solid #e2e8f0; }
.hoverable-card:hover { border-color: #3b82f6; background-color: #eff6ff; }
.card-head-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem; }
.space-between { justify-content: space-between; }
.icon-bubble { width: 40px; height: 40px; border-radius: 50%; background-color: #eff6ff; display: flex; align-items: center; justify-content: center; }
.desc-text { font-size: 0.875rem; color: #64748b; line-height: 1.5; }

/* Inputs & Forms */
.field-group { display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.875rem; }
.input { padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 6px; width: 100%; }

/* Buttons */
.btn { padding: 0.5rem 1rem; border-radius: 6px; font-weight: 500; font-size: 0.875rem; cursor: pointer; border: none; transition: background 0.2s; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:hover { background-color: #1e293b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-ghost { background: transparent; color: #0f172a; }
.btn-ghost:hover { background-color: #f1f5f9; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-success { background-color: #16a34a; color: white; }
.btn-destructive { background-color: #dc2626; color: white; }
.btn-icon { padding: 0.5rem; border-radius: 6px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: flex; align-items: center; justify-content: center; }

/* Badges & Status */
.badge { display: inline-flex; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; background-color: #f1f5f9; color: #475569; }
.badge-primary { background-color: #eff6ff; color: #1d4ed8; }
.badge-signals { display: flex; align-items: center; }
.bg-success { background-color: #dcfce7; color: #166534; }
.bg-destructive { background-color: #fee2e2; color: #991b1b; }

/* Signal Boxes */
.signal-box { padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; background-color: #f8fafc; }
.signal-box.active { border-color: #bbf7d0; background-color: #f0fdf4; }
.status-dot { width: 12px; height: 12px; border-radius: 50%; margin: 0 auto 0.5rem; background-color: #cbd5e1; }
.signal-box.active .status-dot { background-color: #22c55e; }

/* Gesture Selection */
.gesture-card { padding: 1rem; text-align: center; transition: all 0.2s; border: 1px solid #e2e8f0; cursor: pointer; }
.gesture-card.selected { border-color: #3b82f6; background-color: #eff6ff; }
.gesture-card:hover { border-color: #93c5fd; }

/* Waiting Pulse */
.flex-center { display: flex; justify-content: center; align-items: center; height: 100%; }
.pulse-ring { width: 64px; height: 64px; background-color: #eff6ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; animation: pulse-ring 2s infinite; }
.code-display { font-family: monospace; font-size: 2rem; letter-spacing: 0.1em; background: #f1f5f9; padding: 0.5rem 1.5rem; border-radius: 8px; font-weight: 700; }

@keyframes pulse-ring {
    0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
    70% { box-shadow: 0 0 0 20px rgba(59, 130, 246, 0); }
    100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}

/* Dashboard Layout */
.grid-dashboard { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 1024px) {
    .grid-dashboard { grid-template-columns: 2fr 1fr; }
}
.side-widgets { display: flex; flex-direction: column; gap: 1.5rem; }
.badge-running { background-color: #dcfce7; color: #166534; }
.badge-paused { background-color: #fef3c7; color: #92400e; }
.badge-finished { background-color: #dbeafe; color: #1e40af; }
.badge-connected { background-color: #f3e8ff; color: #6b21a8; }

/* Icons */
.icon { width: 1.25rem; height: 1.25rem; }
.icon-sm { width: 1rem; height: 1rem; }
.icon-xs { width: 0.75rem; height: 0.75rem; }
.icon-lg { width: 2rem; height: 2rem; }
.text-primary { color: #2563eb; }
.text-success { color: #16a34a; }
.text-destructive { color: #dc2626; }
.alert-box { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background-color: #fee2e2; border-radius: 6px; color: #991b1b; font-size: 0.875rem; }
.flex-row-between { display: flex; justify-content: space-between; align-items: center; }
.code-block { font-family: monospace; font-weight: 700; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 1.1rem; }
</style>
