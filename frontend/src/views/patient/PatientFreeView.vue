<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import GestureProgress from '../../components/patient/GestureProgress.vue'
import RadialTimer from '../../components/patient/RadialTimer.vue'
import PatientHandVisualization from '../../components/patient/PatientHandVisualization.vue'
import PauseButton from '../../components/common/PauseButton.vue'
import { ALL_GESTURES } from '../../lib/constants'
import type { Gesture } from '../../lib/constants'
import { ChevronRight, Play, Pause, ArrowLeft, Activity, RefreshCw, Maximize, CheckCircle2 } from 'lucide-vue-next'

const emgSignals = ref([
    { id: 1, status: 'active' }, { id: 2, status: 'active' }, { id: 3, status: 'active' }
])

type Step = 'mode-selection' | 'setup' | 'protocols' | 'training' | 'completed'
const step = ref<Step>('mode-selection')
type TrainingMode = 'TLC' | 'LLC'
const trainingMode = ref<TrainingMode>('TLC')

const patientName = ref('')
const patientAge = ref('')
const selectedGestures = ref<Gesture[]>([])

const gestures = ref<Gesture[]>([])
const currentStep = ref(0)
const isExecuting = ref(false)
const timer = ref(5)
const completedSteps = ref<number[]>([])

// Auto Flow State
const isCountingDown = ref(false)
const countdownTimer = ref(3)
const isResting = ref(false)
const restTimer = ref(5)

const activeSignals = computed(() => emgSignals.value.filter(s => s.status === 'active').length)
const currentGesture = computed(() => gestures.value[currentStep.value])
const nextGesture = computed(() => gestures.value[currentStep.value + 1] || null)

const selectMode = (mode: TrainingMode) => {
    trainingMode.value = mode
    step.value = 'setup'
    // In LLC mode, we might want to pre-select gestures or change the UI, 
    // but for now we follow the user instruction to just add the selection screen.
}

const toggleGesture = (g: Gesture) => {
    if (selectedGestures.value.find(sel => sel.id === g.id)) {
        selectedGestures.value = selectedGestures.value.filter(sel => sel.id !== g.id)
    } else {
        selectedGestures.value.push(g)
    }
}

const startTraining = () => {
    gestures.value = [...selectedGestures.value]
    step.value = 'protocols'
    currentStep.value = 0
    completedSteps.value = []
}

const startTrainingByFlow = () => {
    startCountdown()
}

let intervalId: number

const startCountdown = () => {
    isCountingDown.value = true
    isResting.value = false
    isExecuting.value = false
    countdownTimer.value = 3
    runTimer('countdown')
}

const startExecution = () => {
    isExecuting.value = true
    timer.value = 5
    runTimer('execution')
}

const completeGesture = () => {
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
    runTimer('rest')
}

const resetSession = () => {
    step.value = 'mode-selection'
    selectedGestures.value = []
    patientName.value = ''
    patientAge.value = ''
    isResting.value = false
    isCountingDown.value = false
}

const confirmProtocols = () => {
    enterFullscreen()
    step.value = 'training'
    currentStep.value = 0
    completedSteps.value = []
    startTrainingByFlow()
}

const backToModeSelection = () => {
    step.value = 'mode-selection'
}

// Controls
const isPaused = ref(false)

const togglePause = () => {
    if (isPaused.value) {
        isPaused.value = false
        resumeTimer()
    } else {
        isPaused.value = true
        clearInterval(intervalId)
    }
}

const resumeTimer = () => {
    if (isCountingDown.value) {
        runTimer('countdown')
    } else if (isExecuting.value) {
        runTimer('execution')
    } else if (isResting.value) {
        runTimer('rest')
    }
}

const runTimer = (phase: 'countdown' | 'execution' | 'rest') => {
    clearInterval(intervalId)
    intervalId = window.setInterval(() => {
        if (phase === 'countdown') {
            countdownTimer.value--
            if (countdownTimer.value <= 0) {
                clearInterval(intervalId)
                isCountingDown.value = false
                startExecution()
            }
        } else if (phase === 'execution') {
            timer.value--
            if (timer.value <= 0) {
                completeGesture()
            }
        } else if (phase === 'rest') {
            restTimer.value--
            if (restTimer.value <= 0) {
                clearInterval(intervalId)
                currentStep.value++
                startCountdown()
            }
        }
    }, 1000)
}

const enterFullscreen = () => {
    const elem = document.documentElement
    if (elem.requestFullscreen) {
        elem.requestFullscreen().catch((err) => {
            console.warn('Error attempting to enable fullscreen:', err)
        })
    }
}

onUnmounted(() => clearInterval(intervalId))
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Sesión Libre" subtitle="Entrenamiento independiente y exploración" />
    
    <div class="content">
        <!-- MODE SELECTION PHASE -->
        <div v-if="step === 'mode-selection'" class="container-sm">
             <div class="mb-6">
                <router-link to="/patient" class="btn-ghost mb-2">
                    <ArrowLeft class="icon-sm mr-2" /> Volver
                </router-link>
             </div>

             <div class="mb-6">
                 <h2 class="text-xl font-bold text-slate-900 mb-2">Seleccionar Modo de Entrenamiento</h2>
                 <p class="text-slate-500">Elija la metodología que mejor se adapte a su sesión actual.</p>
             </div>

             <div class="grid-2 gap-6">
                 <!-- TLC Card -->
                 <div class="mode-card" @click="selectMode('TLC')">
                     <div class="icon-wrapper blue">
                         <Activity class="w-8 h-8 text-blue-600" />
                     </div>
                     <div class="mode-content">
                         <h3 class="font-bold text-lg text-slate-900 mb-2">Modo Guiado (TLC)</h3>
                         <p class="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Teacher-Led Control</p>
                         <p class="text-sm text-slate-600 leading-relaxed">
                             Usted define los gestos, repeticiones y tiempos. Ideal para sesiones supervisadas donde el usuario decide qué practicar.
                         </p>
                     </div>
                 </div>

                 <!-- LLC Card -->
                 <div class="mode-card" @click="selectMode('LLC')">
                     <div class="icon-wrapper indigo">
                         <RefreshCw class="w-8 h-8 text-indigo-600" />
                     </div>
                     <div class="mode-content">
                         <h3 class="font-bold text-lg text-slate-900 mb-2">Modo Autónomo (LLC)</h3>
                         <p class="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Learner-Led Control</p>
                         <p class="text-sm text-slate-600 leading-relaxed">
                             El sistema presenta gestos de forma adaptativa basándose en la dificultad. El paciente controla el flujo de aprendizaje.
                         </p>
                     </div>
                     <div class="badge-tag">Nuevo</div>
                 </div>
             </div>
        </div>

        <!-- SETUP PHASE -->
        <div v-else-if="step === 'setup'" class="container-sm">
             <div class="mb-6">
                <button class="btn-ghost mb-2" @click="backToModeSelection">
                    <ArrowLeft class="icon-sm mr-2" /> Cambiar Modo
                </button>
             </div>

             <div class="card p-6 mb-6">
                 <div class="flex-row-between mb-4">
                     <h3 class="card-title text-slate-900 font-bold">Configuración de Sesión</h3>
                     <span class="badge badge-neutral">Mode: {{ trainingMode === 'TLC' ? 'Teacher-Led' : 'Learner-Led' }}</span>
                 </div>
                 <div class="grid-2 gap-4">
                     <div class="field">
                         <label class="label">Nombre del Paciente</label>
                         <input v-model="patientName" placeholder="Opcional" class="input" />
                     </div>
                     <div class="field">
                         <label class="label">Edad</label>
                         <input v-model="patientAge" type="number" placeholder="Opcional" class="input" />
                     </div>
                 </div>
             </div>

             <!-- Gestures -->
             <div class="card p-6 mb-6">
                 <div class="flex-row-between mb-4">
                     <span class="font-bold text-slate-900">Selección de Gestos</span>
                     <span class="badge" :class="selectedGestures.length > 0 ? 'badge-primary' : 'badge-neutral'">
                        {{ selectedGestures.length }} seleccionados
                     </span>
                 </div>
                 <div class="grid-gestures">
                     <div v-for="g in ALL_GESTURES" :key="g.id" 
                          class="gesture-card"
                          :class="{ selected: selectedGestures.find(sel => sel.id === g.id) }"
                          @click="toggleGesture(g)">
                          <span class="font-medium text-sm text-slate-900">{{ g.name }}</span>
                          <span class="text-xs text-slate-500">{{ g.nameEn }}</span>
                     </div>
                 </div>
             </div>

             <!-- Status -->
             <div class="card p-4 flex-row-between mb-6">
                 <div class="flex items-center gap-3">
                     <span class="font-medium text-sm text-slate-700">Estado de Señales</span>
                     <div class="flex gap-1">
                         <div v-for="s in emgSignals" :key="s.id" class="w-2.5 h-2.5 rounded-full" :class="s.status === 'active' ? 'bg-green-500' : 'bg-red-500'"></div>
                     </div>
                 </div>
                 <span class="badge" :class="activeSignals >=3 ? 'badge-success' : 'badge-error'">
                     {{ activeSignals >= 3 ? 'Listo para iniciar' : 'Verificar sensores' }}
                 </span>
             </div>

             <button class="btn btn-primary w-full py-3 justify-center" 
                     :disabled="selectedGestures.length === 0 || activeSignals < 3"
                     @click="startTraining">
                     Iniciar Entrenamiento <ChevronRight class="icon-sm ml-2" />
             </button>
        </div>

        <!-- PROTOCOLS PHASE OJO KEVIN CON ESTO SE DEBE MODIFICAR -->
        <div v-else-if="step === 'protocols'" class="container-sm">
             <div class="card p-8 text-center">
                 <div class="mb-8">
                     <h2 class="text-2xl font-bold text-slate-900 mb-2">Protocolos de Inicio</h2>
                     <p class="text-slate-500">Por favor confirme los siguientes pasos antes de comenzar</p>
                 </div>

                 <div class="grid md:grid-cols-3 gap-6 mb-8">
                     <div class="p-4 bg-slate-50 rounded-xl border border-slate-100 flex flex-col items-center">
                         <div class="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-3">
                             <span class="text-xl">🧴</span>
                         </div>
                         <h3 class="font-bold text-slate-900 mb-1">Limpieza</h3>
                         <p class="text-sm text-slate-500">Limpiar la piel con alcohol para mejorar la señal.</p>
                     </div>
                     
                     <div class="p-4 bg-slate-50 rounded-xl border border-slate-100 flex flex-col items-center">
                         <div class="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mb-3">
                             <div class="text-xl">🧠</div>
                         </div>
                         <h3 class="font-bold text-slate-900 mb-1">Concentración</h3>
                         <p class="text-sm text-slate-500">Mantenga máxima atención durante los ejercicios.</p>
                     </div>

                     <div class="p-4 bg-slate-50 rounded-xl border border-slate-100 flex flex-col items-center">
                         <div class="w-12 h-12 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mb-3">
                             <Maximize class="w-6 h-6" />
                         </div>
                         <h3 class="font-bold text-slate-900 mb-1">Pantalla Completa</h3>
                         <p class="text-sm text-slate-500">La sesión se mostrará en pantalla completa.</p>
                     </div>
                 </div>

                 <button class="btn btn-primary w-full py-4 text-lg justify-center shadow-lg hover:translate-y-[-2px] transition-transform" 
                         @click="confirmProtocols">
                         Entendido, Iniciar Sesión <CheckCircle2 class="ml-2 w-5 h-5" />
                 </button>
             </div>
        </div>

        <!-- TRAINING PHASE -->
        <div v-else-if="step === 'training'" class="container-xl w-full">
            <header class="flex-row-between mb-8">
                <div class="flex gap-2">
                    <span class="badge badge-primary">Sesión Libre</span>
                    <span class="badge badge-neutral">{{ trainingMode }}</span>
                </div>
                <div class="flex items-center gap-3">
                    <span class="text-sm text-slate-500">{{ currentStep + 1 }} / {{ gestures.length }}</span>
                </div>
            </header>

            <GestureProgress :steps="gestures.length" :current-step="currentStep" :completed-steps="completedSteps" class="mb-8" />

            <!-- FOCUS MODE UI -->
            <div class="fixed inset-0 z-50 bg-white flex flex-col items-center justify-center overflow-hidden">
                
                <!-- COUNTDOWN PHASE -->
                <div v-if="isCountingDown" class="flex flex-col items-center justify-center h-screen w-full bg-white z-50 fixed inset-0">
                    <p class="text-[4vw] font-bold text-slate-900 mb-8 uppercase tracking-widest text-center px-4 leading-tight">Estamos listos para comenzar</p>
                    <div class="text-[25vw] leading-none font-black text-blue-600 animate-bounce">
                        {{ countdownTimer }}
                    </div>
                </div>

                <!-- EXECUTION & REST PHASE -->
                <div v-else class="w-full h-full flex flex-col relative animate-in fade-in slide-in-from-bottom-4 duration-500">
                    
                    <!-- Top Info (Rest Timer or Execution Timer) -->
                    <!-- Huge Timer Background -->
                    <div class="absolute inset-0 flex items-center justify-center z-0 pointer-events-none opacity-10">
                         <div v-if="isResting" class="flex flex-col items-center">
                             <div class="text-[30vw] leading-none font-bold text-slate-900">{{ restTimer }}</div>
                             <p class="text-[5vw] font-bold text-slate-400 mt-4 tracking-widest uppercase">DESCANSO</p>
                         </div>
                         <div v-else class="flex flex-col items-center">
                             <div class="text-[40vw] leading-none font-black text-slate-900 font-numeric tracking-tighter">{{ timer }}</div>
                         </div>
                    </div>
                    
                    <div v-if="isPaused" class="absolute inset-0 z-50 flex items-center justify-center bg-white/50 backdrop-blur-sm">
                         <div class="bg-black text-white px-12 py-6 rounded-full animate-pulse shadow-2xl">
                             <span class="text-4xl font-black tracking-widest uppercase">Pausa</span>
                         </div>
                    </div>

                    <!-- Main Content (Centered) -->
                    <div class="flex-1 flex flex-col items-center justify-center p-8 z-10">
                        <!-- Gesture Name -->
                        <div class="text-center mb-12">
                             <h2 class="text-[6rem] leading-tight font-black text-slate-900 tracking-tight">
                                 {{ isResting ? nextGesture?.name : currentGesture?.name }}
                             </h2>
                             <p class="text-4xl text-slate-400 font-light">
                                 {{ isResting ? nextGesture?.nameEn : currentGesture?.nameEn }}
                             </p>
                        </div>

                        <!-- Hand Visualization (Large & Centered or Side) -->
                        <div class="w-[300px] h-[300px] opacity-100 transition-opacity duration-500">
                             <PatientHandVisualization 
                                :gesture="(isResting ? nextGesture?.name : currentGesture?.name) || ''" 
                                :is-active="!isResting" 
                             />
                        </div>
                    </div>

                    <!-- Bottom Bar (Next Gesture Preview during active, or instructions) -->
                    <div class="absolute bottom-0 w-full p-8 bg-white/90 backdrop-blur-sm border-t border-slate-100 flex justify-between items-end">
                        <div v-if="!isResting && nextGesture" class="text-left">
                            <p class="text-xl text-slate-400 font-bold uppercase tracking-widest mb-1">Siguiente Movimiento</p>
                            <div class="flex items-baseline gap-4">
                                <h3 class="text-5xl font-bold text-slate-300">{{ nextGesture.name }}</h3>
                            </div>
                        </div>
                        <div v-else-if="isResting">
                            <!-- During rest we already show next gesture in center -->
                            <p class="text-xl text-slate-400">Respire profundo...</p>
                        </div>
                        
                        <!-- Controls -->
                         <div class="absolute left-1/2 -translate-x-1/2 bottom-8">
                             <PauseButton :is-paused="isPaused" @toggle="togglePause" />
                         </div>

                        <!-- Progress -->
                        <div class="text-right">
                            <p class="text-6xl font-black text-slate-100">{{ currentStep + 1 }}<span class="text-4xl text-slate-100">/{{ gestures.length }}</span></p>
                        </div>
                    </div>
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
                 <p class="text-slate-500 mb-8">Ha completado toda la rutina seleccionada.</p>
                 <button class="btn btn-outline w-full" @click="resetSession">Nueva Sesión</button>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Standard Layout */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; display: flex; flex-direction: column; }
.container-xl { max-width: 1200px; margin: 0 auto; width: 100%; }
.container-sm { max-width: 800px; margin: 0 auto; width: 100%; }
.container-xs { max-width: 440px; margin: 0 auto; width: 100%; margin-top: 4rem; }

.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.p-6 { padding: 1.5rem; }
.p-8 { padding: 2rem; }
.p-10 { padding: 2.5rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-8 { margin-bottom: 2rem; }

/* Grid */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.grid-gestures { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
@media(min-width: 768px) { .grid-gestures { grid-template-columns: repeat(4, 1fr); } }
.grid-layout { display: grid; grid-template-columns: 1fr; }
@media(min-width: 1024px) { .grid-layout { grid-template-columns: 3fr 2fr; } }

/* Inputs & Labels */
.field { display: flex; flex-direction: column; gap: 0.5rem; }
.label { font-size: 0.875rem; font-weight: 500; color: #475569; }
.input { width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; transition: border-color 0.2s; }
.input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }

/* Buttons */
.btn { padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; display: inline-flex; align-items: center; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:hover { background-color: #1e293b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-ghost { background: transparent; color: #64748b; padding: 0.5rem 0.75rem; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; font-size: 0.9rem; }
.btn-ghost:hover { background-color: #f1f5f9; color: #0f172a; }

.btn-play { 
    width: 80px; height: 80px; border-radius: 50%; background-color: #2563eb; color: white; border: none; 
    display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    transition: all 0.2s;
}
.btn-play:hover { transform: scale(1.05); background-color: #1d4ed8; }
.icon-xl { width: 32px; height: 32px; }

/* Gestures */
.gesture-card { text-align: center; padding: 1rem; cursor: pointer; border: 2px solid transparent; background-color: #f8fafc; border-radius: 8px; transition: all 0.2s; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.25rem; }
.gesture-card:hover { background-color: #f1f5f9; }
.gesture-card.selected { border-color: #3b82f6; background-color: #eff6ff; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1); }

/* Mode Cards */
.mode-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 2rem;
    cursor: pointer; transition: all 0.3s ease; display: flex; flex-direction: column; gap: 1.5rem;
    position: relative; overflow: hidden; height: 100%;
}
.mode-card:hover {
    transform: translateY(-4px); box-shadow: 0 10px 30px -10px rgba(0,0,0,0.1); border-color: #cbd5e1;
}
.icon-wrapper {
    width: 3.5rem; height: 3.5rem; border-radius: 12px; display: flex; align-items: center; justify-content: center;
}
.icon-wrapper.blue { background-color: #eff6ff; }
.icon-wrapper.indigo { background-color: #eef2ff; }

.text-blue-600 { color: #2563eb; }
.text-indigo-600 { color: #4f46e5; }
.badge-tag {
    position: absolute; top: 1.5rem; right: 1.5rem; background-color: #e0e7ff; color: #4338ca;
    padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 700;
}

/* Badges */
.badge { display: inline-flex; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.badge-primary { background-color: #eff6ff; color: #2563eb; }
.badge-neutral { background-color: #f1f5f9; color: #64748b; }
.badge-success { background-color: #dcfce7; color: #16a34a; }
.badge-error { background-color: #fee2e2; color: #dc2626; }

/* Utils */
.flex-row-between { display: flex; justify-content: space-between; align-items: center; }
.flex-center { display: flex; align-items: center; justify-content: center; }
.text-slate-900 { color: #0f172a; }
.text-slate-700 { color: #334155; }
.text-slate-500 { color: #64748b; }
.text-blue-600 { color: #2563eb; }
.bg-green-500 { background-color: #22c55e; }
.bg-red-500 { background-color: #ef4444; }

.icon-sm { width: 1.25rem; height: 1.25rem; }
.ml-2 { margin-left: 0.5rem; }
.mr-2 { margin-right: 0.5rem; }
</style>
