<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import TopHeader from '../../components/common/TopHeader.vue'
import GestureProgress from '../../components/patient/GestureProgress.vue'
import RadialTimer from '../../components/patient/RadialTimer.vue'
import PatientHandVisualization from '../../components/patient/PatientHandVisualization.vue'
import { ALL_GESTURES } from '../../lib/constants'
import type { Gesture } from '../../lib/constants'
import { Wifi, ChevronRight, Play, Maximize, CheckCircle2 } from 'lucide-vue-next'

const router = useRouter()

// --- State ---
const step = ref<'selection' | 'code' | 'protocols' | 'training' | 'completed'>('selection')
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
const restTimer = ref(5)

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
    
    
    step.value = 'protocols'
    currentStep.value = 0
    completedSteps.value = []
}

const confirmProtocols = () => {
    enterFullscreen()
    step.value = 'training'
    startCountdown()
}

const enterFullscreen = () => {
    const elem = document.documentElement
    if (elem.requestFullscreen) {
        elem.requestFullscreen().catch((err) => {
            console.warn('Error attempting to enable fullscreen:', err)
        })
    }
}

// Training Logic
let intervalId: number
const isCountingDown = ref(false)
const countdownTimer = ref(3)

const startCountdown = () => {
    isCountingDown.value = true
    isResting.value = false
    isExecuting.value = false
    countdownTimer.value = 3
    
    intervalId = window.setInterval(() => {
        countdownTimer.value--
        if (countdownTimer.value <= 0) {
            clearInterval(intervalId)
            isCountingDown.value = false
            startStep()
        }
    }, 1000)
}

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
        startRest()
    } else {
        step.value = 'completed'
    }
}

const startRest = () => {
    isResting.value = true
    restTimer.value = 5
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
    startStep()
}

const reset = () => {
    step.value = 'selection'
    sessionCode.value = ''
    completedSteps.value = []
    gestures.value = []
    isResting.value = false
    isCountingDown.value = false
}

const currentGesture = computed(() => gestures.value[currentStep.value] || null)
const nextGesture = computed(() => gestures.value[currentStep.value + 1] || null)

onUnmounted(() => clearInterval(intervalId))
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Sesión de Paciente" subtitle="Entrenamiento supervisado y autónomo" />

    <div class="content flex-center-col">
       <!-- SELECTION PHASE -->
       <div v-if="step === 'selection'" class="container-sm">
           <div class="header-center">
               <h1 class="title-main">Iniciar Nueva Sesión</h1>
               <p class="subtitle-main">Seleccione el modo de operación para comenzar</p>
           </div>
           
           <div class="grid-2 gap-cards">
               <!-- Supervised -->
               <div class="card hoverable-card p-card" @click="selectMode('supervised')">
                    <div class="card-header-row">
                        <div class="icon-circle bg-blue-light text-blue">
                            <Wifi class="icon-md" />
                        </div>
                        <div>
                            <h3 class="card-title-lg">Sesión Supervisada</h3>
                            <p class="text-xs text-muted">Requiere código de médico</p>
                        </div>
                    </div>
                    <p class="text-desc">Conéctese con su terapeuta para una sesión guiada en tiempo real.</p>
                    <div class="text-right"><ChevronRight class="icon-md text-slate-300" /></div>
               </div>

               <!-- Free -->
               <div class="card hoverable-card p-card" @click="selectMode('free')">
                     <div class="card-header-row">
                        <div class="icon-circle bg-indigo-light text-indigo">
                             <span class="emoji-md">👤</span>
                        </div>
                        <div>
                            <h3 class="card-title-lg">Entrenamiento Libre</h3>
                            <p class="text-xs text-muted">Sin supervisión</p>
                        </div>
                    </div>
                    <p class="text-desc">Practique gestos libremente y visualice las señales sEMG.</p>
                    <div class="text-right"><ChevronRight class="icon-md text-slate-300" /></div>
               </div>
           </div>
       </div>

       <!-- CODE PHASE -->
       <div v-else-if="step === 'code'" class="container-xs">
           <div class="card p-large">
               <div class="header-center mb-6">
                   <h2 class="title-section">Código de Sesión</h2>
                   <p class="subtitle-text">Ingrese el código de 7 dígitos proporcionado</p>
               </div>
               
               <div class="mb-8">
                   <input v-model="sessionCode" maxlength="7" placeholder="XXX-XXX" class="input-code" />
               </div>

               <div class="sensor-status-box mb-6">
                    <div class="status-header mb-4">
                        <span class="status-label">Estado de Sensores</span>
                        <span class="badge" :class="activeSignals >= 3 ? 'badge-success' : 'badge-error'">
                            {{ activeSignals >= 3 ? 'Listo' : 'Verificar' }}
                        </span>
                    </div>
                    <div class="sensor-indicators">
                        <div v-for="s in emgSignals" :key="s.id" class="sensor-item">
                            <div class="sensor-dot" :class="s.status==='active'?'bg-green':'bg-red'"></div>
                            <span class="sensor-name">CH{{s.id}}</span>
                        </div>
                    </div>
               </div>

               <div class="actions-row">
                   <button class="btn btn-outline flex-1" @click="step='selection'">Cancelar</button>
                   <button class="btn btn-primary flex-1" 
                           :disabled="sessionCode.length < 4 || activeSignals < 3"
                           @click="connectSession">
                           Conectar
                   </button>
               </div>
           </div>
       </div>

        <!-- PROTOCOLS PHASE -->
        <div v-else-if="step === 'protocols'" class="container-sm">
             <div class="card p-large text-center">
                 <div class="mb-8">
                     <h2 class="title-2xl mb-2">Protocolos de Inicio</h2>
                     <p class="subtitle-text">Por favor confirme los siguientes pasos antes de comenzar</p>
                 </div>

                 <div class="protocols-grid mb-8">
                     <div class="protocol-card">
                         <div class="protocol-icon bg-blue-light text-blue">
                             <span class="emoji-lg">🧴</span>
                         </div>
                         <h3 class="protocol-title">Limpieza</h3>
                         <p class="protocol-desc">Limpiar la piel con alcohol para mejorar la señal.</p>
                     </div>
                     
                     <div class="protocol-card">
                         <div class="protocol-icon bg-indigo-light text-indigo">
                             <span class="emoji-lg">🧠</span>
                         </div>
                         <h3 class="protocol-title">Concentración</h3>
                         <p class="protocol-desc">Mantenga máxima atención durante los ejercicios.</p>
                     </div>

                     <div class="protocol-card">
                         <div class="protocol-icon bg-purple-light text-purple">
                             <Maximize class="icon-md" />
                         </div>
                         <h3 class="protocol-title">Pantalla Completa</h3>
                         <p class="protocol-desc">La sesión se mostrará en pantalla completa.</p>
                     </div>
                 </div>

                 <button class="btn btn-primary w-full py-large flex-center shadow-hover" 
                         @click="confirmProtocols">
                         Entendido, Iniciar Sesión <CheckCircle2 class="icon-sm ml-2" />
                 </button>
             </div>
        </div>

       <!-- TRAINING PHASE (FOCUS MODE) -->
       <div v-else-if="step === 'training'" class="fullscreen-overlay">
            
            <!-- COUNTDOWN PHASE -->
            <div v-if="isCountingDown" class="countdown-container animate-fade-in">
                <p v-if="currentStep === 0" class="countdown-label">Estamos listos para comenzar</p>
                <div class="countdown-number animate-bounce">
                    {{ countdownTimer }}
                </div>
            </div>

            <!-- EXECUTION & REST PHASE -->
            <div v-else class="execution-container animate-slide-up">
                
                <!-- Top Info -->
                <!-- Rest Overlay -->
                <div v-if="isResting" class="rest-overlay-centered">
                     <div class="timer-wrapper">
                         <div class="timer-huge-rest">{{ restTimer }}</div>
                         <p class="timer-label">DESCANSO</p>
                     </div>
                </div>

                <!-- Top Info (Execution) -->
                <div v-else class="top-timer-container">
                     <div class="timer-wrapper">
                         <div class="timer-huge-exec">{{ timer }}</div>
                     </div>
                </div>

                <!-- Main Content (Centered) -->
                <div class="main-content">
                    <!-- Gesture Name -->
                    <div class="gesture-display">
                         <h2 class="gesture-title-main">
                             {{ isResting ? nextGesture?.name : currentGesture?.name }}
                         </h2>
                         <p class="gesture-subtitle-main">
                             {{ isResting ? nextGesture?.nameEn : currentGesture?.nameEn }}
                         </p>
                    </div>

                    <!-- Hand Visualization -->
                    <div class="visualization-box">
                         <PatientHandVisualization 
                            :gesture="(isResting ? nextGesture?.name : currentGesture?.name) || ''" 
                            :is-active="!isResting" 
                         />
                    </div>
                </div>

                <!-- Bottom Bar -->
                <div class="bottom-bar">
                    <div v-if="!isResting && nextGesture" class="next-gesture-info">
                        <p class="next-label">Siguiente Movimiento</p>
                        <div class="next-content">
                            <h3 class="next-name">{{ nextGesture.name }}</h3>
                        </div>
                    </div>
                    <div v-else-if="isResting">
                        <p class="breathing-text">Respire profundo...</p>
                    </div>
                    
                    <!-- Progress -->
                    <div class="progress-info">
                        <p class="progress-number">{{ currentStep + 1 }}<span class="progress-total">/{{ gestures.length }}</span></p>
                    </div>
                </div>
            </div>
       </div>

       <!-- COMPLETED PHASE -->
       <div v-else class="container-xs">
           <div class="card p-extra text-center">
                <div class="success-circle">
                    <span class="check-mark">✓</span>
                </div>
                <h2 class="title-2xl mb-3">Sesión Completada</h2>
                <p class="subtitle-text mb-8">Sus datos han sido guardados correctamente.</p>
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
.flex-center-col { align-items: center; }

/* Containers */
.container-xl { max-width: 1200px; margin: 0 auto; width: 100%; }
.container-sm { max-width: 800px; margin: 0 auto; width: 100%; margin-top: 4rem; }
.container-xs { max-width: 440px; margin: 0 auto; width: 100%; margin-top: 4rem; }

/* Typography */
.text-center { text-align: center; }
.title-main { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; }
.title-2xl { font-size: 1.5rem; font-weight: 700; color: #0f172a; }
.title-section { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem; }
.subtitle-main { color: #64748b; font-size: 1rem; }
.subtitle-text { color: #64748b; font-size: 0.875rem; }
.text-desc { color: #475569; font-size: 0.875rem; margin-bottom: 1rem; line-height: 1.5; }
.text-muted { color: #94a3b8; }
.card-title-lg { font-size: 1.125rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem; }
.text-right { text-align: right; }

/* Cards */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.hoverable-card { transition: all 0.2s; cursor: pointer; }
.hoverable-card:hover { border-color: #3b82f6; transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
.p-card { padding: 1.5rem; }
.p-large { padding: 2rem; }
.p-extra { padding: 2.5rem; }
.header-center { text-align: center; margin-bottom: 2rem; }
.card-header-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }

/* Grid */
.grid-2 { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 768px) { .grid-2 { grid-template-columns: 1fr 1fr; } }
.gap-cards { gap: 1rem; }

/* Icons & Badges */
.icon-circle { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.icon-md { width: 24px; height: 24px; }
.icon-sm { width: 20px; height: 20px; }
.emoji-md { font-size: 1.25rem; }
.emoji-lg { font-size: 1.5rem; }

.bg-blue-light { background-color: #eff6ff; } .text-blue { color: #2563eb; }
.bg-indigo-light { background-color: #eef2ff; } .text-indigo { color: #4f46e5; }
.bg-purple-light { background-color: #f3e8ff; } .text-purple { color: #9333ea; }
.bg-green { background-color: #22c55e; }
.bg-red { background-color: #ef4444; }
.text-slate-300 { color: #cbd5e1; }

.success-circle { width: 4rem; height: 4rem; background-color: #dcfce7; color: #16a34a; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; margin-bottom: 1.5rem; }
.check-mark { font-size: 1.5rem; }

/* Code Input Box */
.input-code { 
    text-align: center; font-family: 'Roboto', monospace; font-size: 2rem; padding: 1rem; width: 100%; 
    border: 2px solid #e2e8f0; border-radius: 12px; letter-spacing: 0.25em; text-transform: uppercase; font-weight: 700; color: #0f172a;
    transition: all 0.2s; box-sizing: border-box;
}
.input-code:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }

/* Sensor Status Box */
.sensor-status-box { background-color: #f8fafc; border-radius: 0.5rem; padding: 1rem; border: 1px solid #f1f5f9; }
.status-header { display: flex; justify-content: space-between; align-items: center; }
.status-label { font-size: 0.875rem; font-weight: 500; color: #334155; }
.sensor-indicators { display: flex; justify-content: center; gap: 1rem; }
.sensor-item { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; }
.sensor-dot { width: 0.75rem; height: 0.75rem;border-radius: 50%; }
.sensor-name { font-size: 0.75rem; color: #94a3b8; font-family: monospace; }
.badge { display: inline-flex; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.badge-success { background-color: #dcfce7; color: #16a34a; }
.badge-error { background-color: #fee2e2; color: #dc2626; }

/* Buttons */
.btn { padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:active { transform: scale(0.98); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-outline:hover { background-color: #f8fafc; }
.py-large { padding-top: 1rem; padding-bottom: 1rem; font-size: 1.125rem; }
.flex-1 { flex: 1; }
.actions-row { display: flex; gap: 0.75rem; }
.shadow-hover:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
.ml-2 { margin-left: 0.5rem; }

/* Protocols Grid */
.protocols-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 768px) { .protocols-grid { grid-template-columns: repeat(3, 1fr); } }
.protocol-card { padding: 1rem; background-color: #f8fafc; border-radius: 0.75rem; border: 1px solid #f1f5f9; display: flex; flex-direction: column; align-items: center; }
.protocol-icon { width: 3rem; height: 3rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem; }
.protocol-title { font-weight: 700; color: #0f172a; margin-bottom: 0.25rem; font-size: 1rem; }
.protocol-desc { font-size: 0.875rem; color: #64748b; }

/* Spacers */
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-8 { margin-bottom: 2rem; }

/* Focus Mode / Fullscreen */
.fullscreen-overlay { position: fixed; inset: 0; z-index: 50; background-color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; width: 100vw; height: 100vh; top: 0; left: 0; }

.countdown-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; width: 100%; }
.countdown-label { font-size: 2.25rem; color: #94a3b8; font-weight: 300; margin-bottom: 2rem; text-transform: uppercase; letter-spacing: 0.1em; text-align: center; }
.countdown-number { font-size: 15rem; line-height: 1; font-weight: 900; color: #0f172a; }

.execution-container { width: 100%; height: 100%; display: flex; flex-direction: column; position: relative; }

.rest-overlay-centered { 
    position: absolute; 
    inset: 0; 
    z-index: 50; 
    background-color: white; 
    display: flex; 
    align-items: center; 
    justify-content: center;
}

.top-timer-container { position: absolute; top: 3rem; left: 0; right: 0; display: flex; justify-content: center; z-index: 0; }
.timer-wrapper { display: flex; flex-direction: column; align-items: center; text-align: center; }
.timer-huge-rest { font-size: 8rem; line-height: 1; font-weight: 700; color: #ef4444; }
.timer-label { font-size: 2.25rem; font-weight: 700; color: #ef4444; margin-top: 0.5rem; letter-spacing: 0.1em; }
.timer-huge-exec { font-size: 12rem; line-height: 1; font-weight: 900; color: #2563eb; font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; }

.main-content { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; z-index: 10; }
.gesture-display { text-align: center; margin-bottom: 3rem; }
.gesture-title-main { font-size: 6rem; line-height: 1.1; font-weight: 900; color: #0f172a; letter-spacing: -0.02em; margin-bottom: 0.5rem; }
.gesture-subtitle-main { font-size: 2.25rem; color: #94a3b8; font-weight: 300; }

.visualization-box { width: 300px; height: 300px; transition: opacity 0.5s; }

.bottom-bar { position: absolute; bottom: 0; width: 100%; padding: 2rem; background-color: rgba(255,255,255,0.9); backdrop-filter: blur(4px); border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: flex-end; box-sizing: border-box; }
.next-label { font-size: 1.25rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem; }
.next-name { font-size: 3rem; font-weight: 700; color: #cbd5e1; margin: 0; }
.breathing-text { font-size: 1.25rem; color: #94a3b8; }
.progress-number { font-size: 3.75rem; font-weight: 900; color: #f1f5f9; margin: 0; }
.progress-total { font-size: 2.25rem; color: #f1f5f9; }
.flex-center { display: flex; align-items: center; justify-content: center; }

/* Animations */
@keyframes bounce { 
    0%, 100% { transform: translateY(-10%); animation-timing-function: cubic-bezier(0.8,0,1,1); }
    50% { transform: none; animation-timing-function: cubic-bezier(0,0,0.2,1); }
}
.animate-bounce { animation: bounce 1s infinite; }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
.animate-fade-in { animation: fade-in 0.3s ease-out forwards; }
@keyframes slide-up { from { opacity: 0; transform: translateY(2rem); } to { opacity: 1; transform: translateY(0); } }
.animate-slide-up { animation: slide-up 0.5s ease-out forwards; }
</style>
