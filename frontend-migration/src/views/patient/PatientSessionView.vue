<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import TopHeader from '../../components/common/TopHeader.vue'
import GestureProgress from '../../components/patient/GestureProgress.vue'
import RadialTimer from '../../components/patient/RadialTimer.vue'
import PatientHandVisualization from '../../components/patient/PatientHandVisualization.vue'
import { ALL_GESTURES } from '../../lib/constants'
import type { Gesture } from '../../lib/constants'
import { Wifi, ChevronRight, Play } from 'lucide-vue-next'

const router = useRouter()

// --- State ---
const step = ref<'selection' | 'code' | 'training' | 'completed'>('selection')
const sessionCode = ref('')
const emgSignals = ref([
    { id: 1, status: 'active' }, { id: 2, status: 'active' }, { id: 3, status: 'active' }
])
const activeSignals = computed(() => emgSignals.value.filter(s => s.status === 'active').length)

// Training Data
const trainingMode = ref<'TLC' | 'LLC' | null>(null)
const gestures = ref<Gesture[]>([])
const currentStep = ref(0)
const completedSteps = ref<number[]>([])

// Execution State
const isExecuting = ref(false)
const timer = ref(5)
const isResting = ref(false)
const restTimer = ref(3)

// Mode Selection
const selectMode = (mode: 'supervised' | 'free') => {
    if (mode === 'free') {
        router.push('/patient/free')
    } else {
        step.value = 'code'
    }
}

// Supervised Logic
const connectSession = () => {
    // Mock simulation
    const mode = Math.random() > 0.5 ? 'TLC' : 'LLC'
    trainingMode.value = mode
    
    if (mode === 'TLC') {
        gestures.value = ALL_GESTURES.slice(0, 4)
    } else {
        gestures.value = [...ALL_GESTURES].sort(() => Math.random() - 0.5)
    }
    
    step.value = 'training'
    currentStep.value = 0
    completedSteps.value = []
}

// Training Logic
let intervalId: number
const startStep = () => {
    isExecuting.value = true
    timer.value = 5
    intervalId = window.setInterval(() => {
        timer.value--
        if (timer.value <= 0) {
            finishStep()
        }
    }, 1000)
}

const finishStep = () => {
    clearInterval(intervalId)
    isExecuting.value = false
    if (!completedSteps.value.includes(currentStep.value)) {
        completedSteps.value.push(currentStep.value)
    }
    
    if (currentStep.value < gestures.value.length - 1) {
        if (trainingMode.value === 'LLC') {
            startRest()
        } else {
            currentStep.value++
            timer.value = 5
        }
    } else {
        step.value = 'completed'
    }
}

const startRest = () => {
    isResting.value = true
    restTimer.value = 3
    intervalId = window.setInterval(() => {
        restTimer.value--
        if (restTimer.value <= 0) {
            endRest()
        }
    }, 1000)
}

const endRest = () => {
    clearInterval(intervalId)
    isResting.value = false
    currentStep.value++
    // Auto start next in LLC (Simulating)
    setTimeout(() => {
        startStep()
    }, 500)
}

const reset = () => {
    step.value = 'selection'
    sessionCode.value = ''
    completedSteps.value = []
    gestures.value = []
    isResting.value = false
}

const currentGesture = computed(() => gestures.value[currentStep.value] || null)

onUnmounted(() => clearInterval(intervalId))
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Sesión de Paciente" subtitle="Entrenamiento supervisado y autónomo" />

    <div class="content flex-center-col">
       <!-- SELECTION PHASE -->
       <div v-if="step === 'selection'" class="container-sm">
           <div class="text-center mb-8">
               <h1 class="text-2xl font-bold text-slate-900">Iniciar Nueva Sesión</h1>
               <p class="text-slate-500">Seleccione el modo de operación para comenzar</p>
           </div>
           
           <div class="grid-2 gap-4">
               <!-- Supervised -->
               <div class="card hoverable-card p-6" @click="selectMode('supervised')">
                    <div class="flex items-center gap-4 mb-4">
                        <div class="icon-circle bg-blue-50 text-blue-600"><Wifi class="icon" /></div>
                        <div>
                            <h3 class="font-bold text-lg text-slate-900">Sesión Supervisada</h3>
                            <p class="text-xs text-muted">Requiere código de médico</p>
                        </div>
                    </div>
                    <p class="text-sm text-slate-600 mb-4">Conéctese con su terapeuta para una sesión guiada en tiempo real.</p>
                    <div class="text-right"><ChevronRight class="icon text-slate-300" /></div>
               </div>

               <!-- Free -->
               <div class="card hoverable-card p-6" @click="selectMode('free')">
                     <div class="flex items-center gap-4 mb-4">
                        <div class="icon-circle bg-indigo-50 text-indigo-600">
                             <div class="text-xl">👤</div>
                        </div>
                        <div>
                            <h3 class="font-bold text-lg text-slate-900">Entrenamiento Libre</h3>
                            <p class="text-xs text-muted">Sin supervisión</p>
                        </div>
                    </div>
                    <p class="text-sm text-slate-600 mb-4">Practique gestos libremente y visualice las señales sEMG.</p>
                    <div class="text-right"><ChevronRight class="icon text-slate-300" /></div>
               </div>
           </div>
       </div>

       <!-- CODE PHASE -->
       <div v-else-if="step === 'code'" class="container-xs">
           <div class="card p-8">
               <div class="text-center mb-6">
                   <h2 class="text-xl font-bold text-slate-900">Código de Sesión</h2>
                   <p class="text-sm text-slate-500">Ingrese el código de 7 dígitos proporcionado</p>
               </div>
               
               <div class="mb-8">
                   <input v-model="sessionCode" maxlength="7" placeholder="XXX-XXX" class="input-code" />
               </div>

               <div class="bg-slate-50 rounded-lg p-4 mb-6 border border-slate-100">
                    <div class="flex justify-between items-center mb-4">
                        <span class="text-sm font-medium text-slate-700">Estado de Sensores</span>
                        <span class="badge" :class="activeSignals >= 3 ? 'badge-success' : 'badge-error'">
                            {{ activeSignals >= 3 ? 'Listo' : 'Verificar' }}
                        </span>
                    </div>
                    <div class="flex justify-center gap-4">
                        <div v-for="s in emgSignals" :key="s.id" class="flex flex-col items-center gap-1">
                            <div class="w-3 h-3 rounded-full" :class="s.status==='active'?'bg-green-500':'bg-red-500'"></div>
                            <span class="text-xs text-slate-400 font-mono">CH{{s.id}}</span>
                        </div>
                    </div>
               </div>

               <div class="flex gap-3">
                   <button class="btn btn-outline flex-1" @click="step='selection'">Cancelar</button>
                   <button class="btn btn-primary flex-1" 
                           :disabled="sessionCode.length < 4 || activeSignals < 3"
                           @click="connectSession">
                           Conectar
                   </button>
               </div>
           </div>
       </div>

       <!-- TRAINING PHASE -->
       <div v-else-if="step === 'training'" class="container-xl w-full">
           <div class="flex justify-between items-center mb-8">
                <div class="flex gap-3">
                    <span class="badge badge-primary">Supervisada</span>
                    <span class="badge badge-neutral">{{ trainingMode === 'TLC' ? 'Modo Guiado' : 'Modo Autónomo' }}</span>
                </div>
                <span class="text-sm font-medium text-slate-500">Gesto {{ currentStep + 1 }} de {{ gestures.length }}</span>
           </div>

           <GestureProgress :steps="gestures.length" :current-step="currentStep" :completed-steps="completedSteps" class="mb-8" />

           <div class="grid-layout gap-8">
               <div class="card col-main relative p-8 flex flex-col items-center justify-center min-h-[400px]">
                    <div class="text-center mb-8">
                        <h2 class="text-4xl font-bold text-slate-900 mb-2">{{ currentGesture?.name }}</h2>
                        <p class="text-xl text-slate-400">{{ currentGesture?.nameEn }}</p>
                    </div>

                    <div v-if="isExecuting || isResting" class="flex flex-col items-center">
                         <RadialTimer :time-remaining="isResting ? restTimer : timer" 
                                      :total-time="isResting ? 3 : 5" 
                                      :is-resting="isResting" />
                         <p class="mt-6 text-lg font-medium" :class="isResting ? 'text-slate-400' : 'text-blue-600'">
                            {{ isResting ? "Relaje el músculo..." : "Mantenga la contracción..." }}
                         </p>
                    </div>

                    <div v-else class="flex flex-col items-center">
                         <button class="btn-play" @click="startStep">
                             <Play class="icon-xl ml-1" />
                         </button>
                         <p class="mt-4 text-slate-500 font-medium">Presione para iniciar</p>
                    </div>
               </div>
               
               <div class="col-side card p-4 bg-slate-50 border-slate-200">
                   <PatientHandVisualization :gesture="currentGesture?.name || ''" :is-active="isExecuting" />
               </div>
           </div>
       </div>

       <!-- COMPLETED PHASE -->
       <div v-else class="container-xs">
           <div class="card p-10 text-center">
                <div class="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                    <span class="text-2xl">✓</span>
                </div>
                <h2 class="text-2xl font-bold text-slate-900 mb-3">Sesión Completada</h2>
                <p class="text-slate-500 mb-8">Sus datos han sido guardados correctamente.</p>
                <button class="btn btn-outline w-full" @click="reset">Volver al Inicio</button>
           </div>
       </div>
    </div>
  </div>
</template>

<style scoped>
/* Standard Layout */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; display: flex; flex-direction: column; }
.flex-center-col { align-items: center; } /* For centering content vertically if needed, mostly for selection/code */

.container-xl { max-width: 1200px; margin: 0 auto; width: 100%; }
.container-sm { max-width: 800px; margin: 0 auto; width: 100%; margin-top: 4rem; }
.container-xs { max-width: 440px; margin: 0 auto; width: 100%; margin-top: 4rem; }

.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.hoverable-card { transition: all 0.2s; cursor: pointer; }
.hoverable-card:hover { border-color: #3b82f6; transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.p-6 { padding: 1.5rem; }
.p-8 { padding: 2rem; }
.p-10 { padding: 2.5rem; }

/* Grid */
.grid-2 { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 768px) { .grid-2 { grid-template-columns: 1fr 1fr; } }
.grid-layout { display: grid; grid-template-columns: 1fr; }
@media(min-width: 1024px) { .grid-layout { grid-template-columns: 3fr 2fr; } }

/* UI Elements */
.icon-circle { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.icon { width: 24px; height: 24px; }
.bg-blue-50 { background-color: #eff6ff; } .text-blue-600 { color: #2563eb; }
.bg-indigo-50 { background-color: #eef2ff; } .text-indigo-600 { color: #4f46e5; }
.bg-green-100 { background-color: #dcfce7; } .text-green-600 { color: #16a34a; }

.input-code { 
    text-align: center; font-family: 'Roboto', monospace; font-size: 2rem; padding: 1rem; width: 100%; 
    border: 2px solid #e2e8f0; border-radius: 12px; letter-spacing: 0.25em; text-transform: uppercase; font-weight: 700; color: #0f172a;
    transition: all 0.2s;
}
.input-code:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }

.btn { padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-play { 
    width: 80px; height: 80px; border-radius: 50%; background-color: #2563eb; color: white; border: none; 
    display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    transition: all 0.2s;
}
.btn-play:hover { transform: scale(1.05); background-color: #1d4ed8; }
.icon-xl { width: 32px; height: 32px; }

.badge { display: inline-flex; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.badge-primary { background-color: #eff6ff; color: #2563eb; }
.badge-neutral { background-color: #f1f5f9; color: #64748b; }
.badge-success { background-color: #dcfce7; color: #16a34a; }
.badge-error { background-color: #fee2e2; color: #dc2626; }

.text-slate-900 { color: #0f172a; }
.text-slate-500 { color: #64748b; }
.text-slate-400 { color: #94a3b8; }
.text-muted { color: #94a3b8; }

.mb-4 { margin-bottom: 1rem; }
.mb-8 { margin-bottom: 2rem; }
.mt-6 { margin-top: 1.5rem; }
</style>
