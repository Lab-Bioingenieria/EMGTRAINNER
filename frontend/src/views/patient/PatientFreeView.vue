<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import GestureProgress from '../../components/patient/GestureProgress.vue'
import RadialTimer from '../../components/patient/RadialTimer.vue'
import PatientHandVisualization from '../../components/patient/PatientHandVisualization.vue'
import PauseButton from '../../components/common/PauseButton.vue'
import { ALL_GESTURES, DEFAULT_DEVICE_ID, API_BASE_URL } from '../../lib/constants'
import type { Gesture } from '../../lib/constants'
import { ChevronRight, Play, Pause, ArrowLeft, Activity, RefreshCw, Maximize, CheckCircle2, FileText, Download } from 'lucide-vue-next'
import { EmgService } from '../../services/emg.service'
import { PatientService } from '../../services/patient.service'

const emgSignals = ref([
    { id: 1, status: 'active' }, { id: 2, status: 'active' }, { id: 3, status: 'active' }
])
const lastSession = ref<any>(null)

type Step = 'mode-selection' | 'setup' | 'protocols' | 'tutorial' | 'training' | 'completed'
const step = ref<Step>('mode-selection')
const tutorialStep = ref(0)
const maxTutorialTime = 4000

// TTS Helper
const speak = (text: string) => {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel()
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = 'es-ES'
        utterance.rate = 1.0
        window.speechSynthesis.speak(utterance)
    }
}
type TrainingMode = 'TLC' | 'LLC'
const trainingMode = ref<TrainingMode>('TLC')

const patientName = ref('')
const patientAge = ref('')
const selectedGestures = ref<Gesture[]>([])
const gestureDuration = ref(5)
const circuitRepetitions = ref(1)

const gestures = ref<Gesture[]>([])
const currentStep = ref(0)
const isExecuting = ref(false)
const timer = ref(5)
const completedSteps = ref<number[]>([])
const currentOrderId = ref<string | null>(null)
const touchedName = ref(false)

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

// API Helper for LLC
const fetchNextGestureSuggestion = async (): Promise<string | null> => {
    try {
        const response = await fetch(`http://localhost:8000/learning/next-gesture/${patientName.value || 'Guest'}`)
        if (response.ok) {
            const data = await response.json()
            return data.next_gesture
        }
    } catch (e) {
        console.error("Error fetching next gesture:", e)
    }
    return null
}

const getNextGesture = async (): Promise<Gesture> => {
    let nextName: string | null = null
    
    // Always fetch from backend in LLC
    nextName = await fetchNextGestureSuggestion()
    
    // Fallback or Random if null
    if (!nextName) {
        // Pick random that isn't the immediate last one
        const last = gestures.value.length > 0 ? gestures.value[gestures.value.length - 1] : null
        const candidates = ALL_GESTURES.filter(g => g.name !== last?.name)
        const random = candidates[Math.floor(Math.random() * candidates.length)]
        return random
    }
    
    // Find gesture object by name
    const found = ALL_GESTURES.find(g => g.name === nextName)
    return found || ALL_GESTURES[0] // Should exist
}

const startTraining = async () => {
    try {
        const order = await PatientService.createOrder({
            device_id: DEFAULT_DEVICE_ID,
            signal_types: ['EMG'], // Default
            notes: `Training Mode: ${trainingMode.value}, Patient: ${patientName.value}`
        })
        currentOrderId.value = order.id
    } catch (error) {
        console.error("Failed to create order (running offline):", error)
        // Fallback for offline mode or server error
        currentOrderId.value = `local-${Date.now()}`
    }

    if (trainingMode.value === 'LLC') {
        // Initialize with Dynamic Gestures
        gestures.value = []
        gestures.value.push(await getNextGesture())
        gestures.value.push(await getNextGesture())
    } else {
        // TLC Mode: Use selected gestures
        const circuit = [...selectedGestures.value]
        let expanded: Gesture[] = []
        for(let i=0; i < circuitRepetitions.value; i++) {
            expanded = expanded.concat(circuit)
        }
        gestures.value = expanded
    }

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
    if(gestures.value[currentStep.value]) {
        const gestureName = gestures.value[currentStep.value].name
        EmgService.setMovementLabel(gestureName)
        speak(gestureName)
    }
    timer.value = gestureDuration.value
    runTimer('execution')
}

const completeGesture = async () => {
    clearInterval(intervalId)
    isExecuting.value = false
    if (!completedSteps.value.includes(currentStep.value)) {
        completedSteps.value.push(currentStep.value)
    }
    
    if (trainingMode.value === 'LLC') {
         // LLC: Always Fetch Next and Continue
         const next = await getNextGesture()
         gestures.value.push(next)
         startRest()
    } else {
        // TLC: Check if finished
        if (currentStep.value < gestures.value.length - 1) {
            startRest()
        } else {
            // Stop EMG Session and Get CSV
            try {
                await EmgService.stopSession()
                // Small delay to ensure file write
                setTimeout(async () => {
                    lastSession.value = await EmgService.getLatestSession()
                }, 500)
            } catch (e) {
                console.error("Failed to stop session", e)
            }

            step.value = 'completed'
        }
    }
}

const startRest = () => {
    isResting.value = true
    EmgService.setMovementLabel('Rest')
    
    // Check if a circuit loop just finished
    // currentStep is the index of the gesture just completed.
    // If the next step index (currentStep + 1) is a multiple of the circuit length (selectedGestures.length),
    // then we just finished one full circuit loop.
    const circuitLength = selectedGestures.value.length // Only relevant in TLC mode mostly
    const nextStepIndex = currentStep.value + 1
    
    if (trainingMode.value === 'TLC' && circuitLength > 0 && nextStepIndex % circuitLength === 0) {
        speak("Circuito completado. Baje la mano.")
    } else {
        speak("Descansa")
    }

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

const startTutorial = () => {
    step.value = 'tutorial'
    currentStep.value = 0
    tutorialStep.value = 0
    enterFullscreen()
    speak("Bienvenido. Haremos un breve repaso de los movimientos.")
    setTimeout(playTutorialStep, 3500)
}

const playTutorialStep = () => {
    if (tutorialStep.value < selectedGestures.value.length) {
        const gesture = selectedGestures.value[tutorialStep.value]
        speak(`Movimiento: ${gesture.name}. Prepárate.`)
        // Auto-advance logic
        setTimeout(() => {
             if (step.value === 'tutorial') nextTutorialStep()
        }, maxTutorialTime)
    } else {
        finishTutorial()
    }
}

const nextTutorialStep = () => {
    tutorialStep.value++
    if (tutorialStep.value < selectedGestures.value.length) {
        playTutorialStep()
    } else {
        finishTutorial()
    }
}

const finishTutorial = () => {
    speak("Tutorial completado. Iniciando entrenamiento.")
    setTimeout(() => {
        step.value = 'training'
        currentStep.value = 0
        completedSteps.value = []
        startTrainingByFlow()
    }, 2000)
}

const skipTutorial = () => {
    window.speechSynthesis.cancel()
    finishTutorial()
}

const confirmProtocols = async () => {
    if (currentOrderId.value) {
        try {
            await PatientService.startOrder(currentOrderId.value)
        } catch (error) {
            console.error("Failed to start order:", error)
        }
    }
    
    // Start EMG Data Collection
    try {
        await EmgService.setSessionInfo(patientName.value)
        await EmgService.startSession()
    } catch (e) {
        console.error("Failed to start EMG session", e)
    }

    startTutorial()
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
                isResting.value = false
                startExecution()
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

let pollingInterval: number

const updateDeviceStatus = async () => {
    try {
        const status = await EmgService.getDeviceStatus(DEFAULT_DEVICE_ID)
        
        if (status.is_online) {
            emgSignals.value = emgSignals.value.map(s => ({ ...s, status: 'active' }))
        } else {
            emgSignals.value = emgSignals.value.map(s => ({ ...s, status: 'inactive' }))
            
            // Try auto-reconnect on each poll if offline
            // This is "silent" reconnection
            try {
                await EmgService.connect()
            } catch (ignore) {
                // Ignore errors during silent reconnect attempts
            }
        }
    } catch (e) {
        console.error("Status check failed", e)
    }
}

import { onMounted } from 'vue'

onMounted(async () => {
    await updateDeviceStatus()
    
    // Auto-connect if offline
    const initialStatus = await EmgService.getDeviceStatus(DEFAULT_DEVICE_ID)
    if (!initialStatus.is_online) {
        console.log("Device offline, attempting auto-mount connection...")
        try {
            await EmgService.connect()
            await updateDeviceStatus() // Refresh status after connect attempt
        } catch (e) {
            console.error("Auto-connect failed", e)
        }
    }

    pollingInterval = window.setInterval(updateDeviceStatus, 1000)
})

onUnmounted(() => {
    clearInterval(intervalId)
    clearInterval(pollingInterval)
})
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Sesión Libre" subtitle="Entrenamiento independiente y exploración" />
    
    <div class="content">
        <!-- MODE SELECTION PHASE -->
        <div v-if="step === 'mode-selection'" class="container-sm">
             <div class="nav-section">
                <router-link to="/patient" class="btn-ghost">
                    <ArrowLeft class="icon-sm mr-2" /> Volver
                </router-link>
             </div>

             <div class="header-section">
                 <h2 class="title-primary">Seleccionar Modo de Entrenamiento</h2>
                 <p class="subtitle-text">Elija la metodología que mejor se adapte a su sesión actual.</p>
             </div>

             <div class="grid-2 gap-cards">
                 <!-- TLC Card -->
                 <div class="mode-card" @click="selectMode('TLC')">
                     <div class="icon-wrapper blue">
                         <Activity class="icon-lg text-blue" />
                     </div>
                     <div class="mode-content">
                         <h3 class="mode-title">Modo Guiado (TLC)</h3>
                         <p class="mode-subtitle">Teacher-Led Control</p>
                         <p class="mode-description">
                             Usted define los gestos, repeticiones y tiempos. Ideal para sesiones supervisadas donde el usuario decide qué practicar.
                         </p>
                     </div>
                 </div>

                 <!-- LLC Card -->
                 <div class="mode-card" @click="selectMode('LLC')">
                     <div class="icon-wrapper indigo">
                         <RefreshCw class="icon-lg text-indigo" />
                     </div>
                     <div class="mode-content">
                         <h3 class="mode-title">Modo Autónomo (LLC)</h3>
                         <p class="mode-subtitle">Learner-Led Control</p>
                         <p class="mode-description">
                             El sistema presenta gestos de forma adaptativa basándose en la dificultad. El paciente controla el flujo de aprendizaje.
                         </p>
                     </div>
                     <div class="badge-tag">Nuevo</div>
                 </div>
             </div>
        </div>

        <!-- SETUP PHASE -->
        <div v-else-if="step === 'setup'" class="container-sm">
             <div class="nav-section">
                <button class="btn-ghost" @click="backToModeSelection">
                    <ArrowLeft class="icon-sm mr-2" /> Cambiar Modo
                </button>
             </div>

             <div class="card p-content section-spacer">
                 <div class="flex-row-between mb-4">
                     <h3 class="card-title">Configuración de Sesión</h3>
                     <span class="badge badge-neutral">Mode: {{ trainingMode === 'TLC' ? 'Teacher-Led' : 'Learner-Led' }}</span>
                 </div>
                 <div class="grid-2 gap-input">
                     <div class="field">
                         <label class="label">Nombre del Paciente <span class="text-red">*</span></label>
                         <input v-model="patientName" placeholder="Requerido" class="input" :class="{ 'input-error': !patientName && touchedName }" @blur="touchedName = true" />
                     </div>
                     <div class="field">
                          <label class="label">Edad</label>
                          <input v-model="patientAge" type="number" placeholder="Opcional" class="input" />
                      </div>
                  </div>
                  <!-- New Configuration Row -->
                  <div class="grid-2 gap-input mt-4">
                      <div class="field">
                          <label class="label">Duración por Gesto (s)</label>
                          <input v-model.number="gestureDuration" type="number" min="1" max="60" class="input" />
                      </div>
                      <div class="field">
                          <label class="label">Repeticiones del Circuito</label>
                          <input v-model.number="circuitRepetitions" type="number" min="1" max="10" class="input" />
                      </div>
                  </div>
             </div>

             <!-- Gestures (Only for TLC) -->
             <div v-if="trainingMode === 'TLC'" class="card p-content section-spacer">
                 <div class="flex-row-between mb-4">
                     <span class="card-title">Selección de Gestos</span>
                     <span class="badge" :class="selectedGestures.length > 0 ? 'badge-primary' : 'badge-neutral'">
                        {{ selectedGestures.length }} seleccionados
                     </span>
                 </div>
                 <div class="grid-gestures">
                     <div v-for="g in ALL_GESTURES" :key="g.id" 
                          class="gesture-card"
                          :class="{ selected: selectedGestures.find(sel => sel.id === g.id) }"
                          @click="toggleGesture(g)">
                          <span class="gesture-name">{{ g.name }}</span>
                          <span class="gesture-sub">{{ g.nameEn }}</span>
                     </div>
                 </div>
             </div>

             <!-- Status -->
             <div class="card p-small flex-row-between section-spacer">
                 <div class="signal-status">
                     <span class="status-label">Estado de Señales</span>
                     <div class="signal-indicators">
                         <div v-for="s in emgSignals" :key="s.id" class="signal-dot" :class="s.status === 'active' ? 'bg-green' : 'bg-red'"></div>
                     </div>
                 </div>
                 <span class="badge" :class="activeSignals >=3 ? 'badge-success' : 'badge-error'">
                     {{ activeSignals >= 3 ? 'Sensores Conectados' : 'Sensores Desconectados' }}
                 </span>
             </div>

             <button class="btn btn-primary w-full py-action flex-center" 
                     :disabled="(!patientName.trim()) || (trainingMode === 'TLC' && selectedGestures.length === 0)"
                     @click="startTraining">
                     Iniciar Entrenamiento <ChevronRight class="icon-sm ml-2" />
             </button>
        </div>

        <!-- PROTOCOLS PHASE -->
        <div v-else-if="step === 'protocols'" class="container-sm">
             <div class="card p-large text-center">
                 <div class="protocol-header">
                     <h2 class="title-primary">Protocolos de Inicio</h2>
                     <p class="subtitle-text">Por favor confirme los siguientes pasos antes de comenzar</p>
                 </div>

                 <div class="protocol-grid">
                     <div class="protocol-item warning-mode">
                         <div class="emoji-icon"><span>🧠</span></div>
                         <h3>Concentración</h3>
                         <p>Mantenga máxima atención durante los ejercicios.</p>
                     </div>

                     <div class="protocol-item warning-mode">
                         <div class="emoji-icon"><span>🖥️</span></div>
                         <h3>Pantalla Completa</h3>
                         <p>La sesión se mostrará en pantalla completa.</p>
                     </div>
                 </div>

                 <button class="btn btn-primary w-full py-large flex-center shadow-btn" 
                         @click="confirmProtocols">
                         Entendido, Iniciar Sesión <CheckCircle2 class="ml-2 icon-md" />
                 </button>
             </div>
        </div>

        <!-- TUTORIAL PHASE -->
        <div v-else-if="step === 'tutorial'" class="container-sm">
             <div class="card p-extra text-center tutorial-card">
                 <h2 class="title-primary mb-2">Tutorial de Movimientos</h2>
                 <p class="subtitle-text mb-8">Observe y prepárese para realizar los siguientes gestos.</p>

                 <div class="tutorial-highlight mb-8">
                      <div class="tutorial-vis-wrapper">
                         <PatientHandVisualization 
                            :gesture="selectedGestures[tutorialStep]?.name || ''" 
                            :is-active="true" 
                         />
                      </div>
                      <h3 class="gesture-title-large">
                          {{ selectedGestures[tutorialStep]?.name || 'Finalizando...' }}
                      </h3>
                      <p class="gesture-subtitle">
                          {{ selectedGestures[tutorialStep]?.nameEn }}
                      </p>
                 </div>

                 <div class="tutorial-progress">
                     <div class="progress-bar-bg">
                         <div class="progress-bar-fill" 
                              :style="{ width: `${((tutorialStep) / selectedGestures.length) * 100}%` }">
                         </div>
                     </div>
                     <p class="progress-text">{{ tutorialStep + 1 }} de {{ selectedGestures.length }}</p>
                 </div>

                 <button class="btn btn-outline w-full mt-8" @click="skipTutorial">
                     Saltar Tutorial
                 </button>
             </div>
        </div>

        <!-- TRAINING PHASE -->
        <div v-else-if="step === 'training'" class="container-xl w-full">
            <header class="flex-row-between mb-8">
                <div class="session-tags">
                    <span class="badge badge-primary">Sesión Libre</span>
                    <span class="badge badge-neutral">{{ trainingMode }}</span>
                </div>
                <div class="step-indicator">
                    <span class="step-text">{{ currentStep + 1 }} / {{ gestures.length }}</span>
                </div>
            </header>

            <GestureProgress :steps="gestures.length" :current-step="currentStep" :completed-steps="completedSteps" class="progress-bar-container" />

            <!-- FOCUS MODE UI -->
            <div class="focus-overlay">
                
                <!-- COUNTDOWN PHASE -->
                <div v-if="isCountingDown" class="countdown-container">
                    <p v-if="currentStep === 0" class="countdown-label">Estamos listos para comenzar</p>
                    <div class="countdown-number animate-bounce">
                        {{ countdownTimer }}
                    </div>
                </div>

                <!-- EXECUTION & REST PHASE -->
                <div v-else class="execution-container animate-fade-in">
                    
                    <!-- Top Info (Rest Timer or Execution Timer) -->
                    <!-- Rest Overlay Timer (High Z-Index, Centered) -->
                    <div v-if="isResting" class="rest-overlay">
                         <div class="timer-wrapper">
                             <div class="huge-timer">{{ restTimer }}</div>
                             <p class="timer-label">DESCANSO</p>
                         </div>
                    </div>

                    <!-- Execution Background Timer (Low Z-Index, Left Aligned) -->
                    <div v-else class="background-timer">
                         <div class="timer-wrapper">
                             <div class="huge-timer-exec">{{ timer }}</div>
                         </div>
                    </div>
                    
                    <div v-if="isPaused" class="paused-overlay">
                         <div class="paused-badge">
                             <span class="paused-text">Pausa</span>
                         </div>
                    </div>

                    <!-- Main Content (Grid) -->
                    <div class="main-visual-content">
                        <!-- Left Side: Gesture Name & Info -->
                        <div class="gesture-info-side">
                             <h2 class="gesture-title-main">
                                 {{ isResting ? nextGesture?.name : currentGesture?.name }}
                             </h2>
                             <p class="gesture-subtitle-main">
                                 {{ isResting ? nextGesture?.nameEn : currentGesture?.nameEn }}
                             </p>
                        </div>

                        <!-- Right Side: Hand Visualization -->
                        <div class="visualization-side">
                            <div class="visualization-wrapper">
                                 <PatientHandVisualization 
                                    :gesture="(isResting ? nextGesture?.name : currentGesture?.name) || ''" 
                                    :is-active="!isResting" 
                                 />
                            </div>
                        </div>
                    </div>

                    <!-- Bottom Bar -->
                    <div class="bottom-control-bar">
                        <div v-if="!isResting && nextGesture" class="next-gesture-preview">
                            <p class="preview-label">Siguiente Movimiento</p>
                            <div class="preview-content">
                                <h3 class="preview-name">{{ nextGesture.name }}</h3>
                            </div>
                        </div>
                        <div v-else-if="isResting" class="rest-instruction">
                            <p class="instruction-text">Respire profundo...</p>
                        </div>
                        
                        <!-- Controls -->
                         <div class="controls-wrapper">
                             <PauseButton :is-paused="isPaused" @toggle="togglePause" />
                         </div>

                        <!-- Progress -->
                        <div class="progress-display">
                            <p class="progress-text">{{ currentStep + 1 }}<span class="progress-total">/{{ gestures.length }}</span></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- COMPLETED PHASE -->
        <div v-else class="container-xs">
            <div class="card p-extra text-center">
                 <div class="success-icon-wrapper">
                     <span class="success-check">✓</span>
                 </div>
                 <h2 class="title-primary mb-3">Sesión Completada</h2>
                 <p class="subtitle-text mb-8">Ha completado toda la rutina seleccionada.</p>
                 
                 <!-- CSV Result Display -->
                 <div v-if="lastSession" class="csv-result-card mb-8">
                     <div class="csv-icon-box">
                         <FileText class="icon-md text-green" />
                     </div>
                     <div class="csv-info">
                         <p class="csv-name">{{ lastSession.filename }}</p>
                         <p class="csv-meta">{{ (lastSession.size_bytes / 1024).toFixed(1) }} KB • {{ new Date(lastSession.created_at).toLocaleTimeString() }}</p>
                     </div>
                     <a :href="`${API_BASE_URL}/storage/sessions/${lastSession.filename}`" 
                        download 
                        class="btn-icon-only"
                        title="Descargar CSV">
                         <Download class="icon-sm" />
                     </a>
                 </div>

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

/* CSV Card */
.csv-result-card {
    display: flex; align-items: center; gap: 1rem;
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem;
    text-align: left;
}
.csv-icon-box {
    width: 2.5rem; height: 2.5rem; background: #dcfce7; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
}
.csv-info { flex: 1; min-width: 0; }
.csv-name { font-weight: 600; font-size: 0.9rem; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.csv-meta { font-size: 0.75rem; color: #64748b; }
.btn-icon-only {
    width: 2.25rem; height: 2.25rem; display: flex; align-items: center; justify-content: center;
    border-radius: 6px; color: #475569; transition: all 0.2s;
}
.btn-icon-only:hover { background: #e2e8f0; color: #0f172a; }

/* Text Typography */
.title-primary { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; }
.subtitle-text { color: #64748b; font-size: 1rem; }
.text-center { text-align: center; }

/* Card Components */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.p-content { padding: 1.5rem; }
.p-small { padding: 1rem; }
.p-large { padding: 2rem; }
.p-extra { padding: 2.5rem; }
.card-title { font-size: 1rem; font-weight: 700; color: #0f172a; }

/* Spacers */
.section-spacer { margin-bottom: 1.5rem; }
.nav-section { margin-bottom: 1.5rem; }
.header-section { margin-bottom: 1.5rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-8 { margin-bottom: 2rem; }

/* Grid Systems */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.gap-cards { gap: 1.5rem; }
.gap-input { gap: 1rem; }
.grid-gestures { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
@media(min-width: 768px) { .grid-gestures { grid-template-columns: repeat(4, 1fr); } }

/* Inputs */
.field { display: flex; flex-direction: column; gap: 0.5rem; }
.label { font-size: 0.875rem; font-weight: 500; color: #475569; }
.input { width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; transition: border-color 0.2s; box-sizing: border-box; }
.input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }

/* Buttons */
.btn { padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:hover { background-color: #1e293b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-ghost { background: transparent; color: #64748b; padding: 0.5rem 0.75rem; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; font-size: 0.9rem; cursor: pointer; border: none; }
.btn-ghost:hover { background-color: #f1f5f9; color: #0f172a; }
.shadow-btn { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
.py-action { padding-top: 0.75rem; padding-bottom: 0.75rem; }
.py-large { padding-top: 1rem; padding-bottom: 1rem; font-size: 1.125rem; }

/* Icons */
.icon-sm { width: 1.25rem; height: 1.25rem; }
.icon-md { width: 1.25rem; height: 1.25rem; }
.icon-lg { width: 2rem; height: 2rem; }
.ml-2 { margin-left: 0.5rem; }
.mr-2 { margin-right: 0.5rem; }
.text-blue { color: #2563eb; }
.text-indigo { color: #4f46e5; }
.text-green { color: #22c55e; }
.text-red { color: #ef4444; }

/* Gestures */
.gesture-card { text-align: center; padding: 1rem; cursor: pointer; border: 2px solid transparent; background-color: #f8fafc; border-radius: 8px; transition: all 0.2s; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.25rem; }
.gesture-card:hover { background-color: #f1f5f9; }
.gesture-card.selected { border-color: #3b82f6; background-color: #eff6ff; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1); }
.gesture-name { font-weight: 500; font-size: 0.875rem; color: #0f172a; }
.gesture-sub { font-size: 0.75rem; color: #64748b; }

/* Mode Cards */
.mode-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 2rem;
    cursor: pointer; transition: all 0.3s ease; display: flex; flex-direction: column; gap: 1.5rem;
    position: relative; overflow: hidden; height: 100%;
}
.mode-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px -10px rgba(0,0,0,0.1); border-color: #cbd5e1; }
.icon-wrapper { width: 3.5rem; height: 3.5rem; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.icon-wrapper.blue { background-color: #eff6ff; }
.icon-wrapper.indigo { background-color: #eef2ff; }
.mode-title { font-weight: 700; font-size: 1.125rem; color: #0f172a; margin-bottom: 0.5rem; }
.mode-subtitle { font-size: 0.75rem; font-weight: 600; color: #94a3b8; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
.mode-description { font-size: 0.875rem; color: #475569; line-height: 1.6; }
.badge-tag { position: absolute; top: 1.5rem; right: 1.5rem; background-color: #e0e7ff; color: #4338ca; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 700; }

/* Badges */
.badge { display: inline-flex; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.badge-primary { background-color: #eff6ff; color: #2563eb; }
.badge-neutral { background-color: #f1f5f9; color: #64748b; }
.badge-success { background-color: #dcfce7; color: #16a34a; }
.badge-error { background-color: #fee2e2; color: #dc2626; }

/* Signal Status */
.signal-status { display: flex; align-items: center; gap: 0.75rem; }
.status-label { font-weight: 500; font-size: 0.875rem; color: #334155; }
.signal-indicators { display: flex; gap: 0.25rem; }
.signal-dot { width: 0.625rem; height: 0.625rem; border-radius: 50%; }
.bg-green { background-color: #22c55e; }
.bg-red { background-color: #ef4444; }

/* Flex Utils */
.flex-row-between { display: flex; justify-content: space-between; align-items: center; }
.flex-center { display: flex; align-items: center; justify-content: center; }
.w-full { width: 100%; }

/* Protocols */
.protocol-header { margin-bottom: 2rem; }
.protocol-grid { display: flex; gap: 1rem; padding: 1rem; justify-content: center; }
.protocol-item { 
    background: #fef2f2; /* red-50 */
    border: 2px solid #ef4444; /* red-500 */
    border-radius: 12px; 
    padding: 2rem; 
    flex: 1; 
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    text-align: center; 
    box-shadow: 0 4px 6px rgba(220, 38, 38, 0.1);
}
.emoji-icon { font-size: 3.5rem; margin-bottom: 1rem; }
.protocol-item h3 { font-size: 1.5rem; font-weight: 800; color: #dc2626; margin-bottom: 0.75rem; text-transform: uppercase; }
.protocol-item p { color: #b91c1c; font-size: 1.1rem; font-weight: 600; line-height: 1.5; }

/* Fullscreen Focus Mode */
.focus-overlay { position: fixed; inset: 0; z-index: 50; background-color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; top: 0; left: 0; width: 100vw; height: 100vh; }
.countdown-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; width: 100%; }
.countdown-label { font-size: 4vw; font-weight: 700; color: #0f172a; margin-bottom: 2rem; text-transform: uppercase; letter-spacing: 0.1em; text-align: center; }
.countdown-number { font-size: 25vw; line-height: 1; font-weight: 900; color: #2563eb; }
.execution-container { width: 100%; height: 100%; display: flex; flex-direction: column; position: relative; }

/* Visual Content Grid Layout */
.main-visual-content { 
    flex: 1; 
    display: grid; 
    grid-template-columns: 1fr 1fr; 
    align-items: center; 
    padding: 2rem 4rem; 
    z-index: 10; 
    max-width: 1600px;
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
}

.gesture-info-side { 
    text-align: left; 
    display: flex; 
    flex-direction: column; 
    justify-content: center;
}

.gesture-title-main { 
    font-size: 5rem; 
    line-height: 1.1; 
    font-weight: 900; 
    color: #0f172a; 
    letter-spacing: -0.02em; 
    margin-bottom: 0.5rem; 
}

.gesture-subtitle-main { 
    font-size: 2rem; 
    color: #64748b; 
    font-weight: 300; 
}

.visualization-side { 
    display: flex; 
    justify-content: center; 
    align-items: center; 
}

.visualization-wrapper { 
    width: 650px; 
    height: 650px; 
    transition: opacity 0.5s; 
}

/* Rest Overlay */
.rest-overlay { 
    position: absolute; 
    inset: 0; 
    z-index: 20; 
    background-color: white; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
}

/* Background Timer - moved slightly to avoid complete overlap if centered */
.background-timer { 
    position: absolute; 
    inset: 0; 
    display: flex; 
    align-items: center; 
    justify-content: flex-start; /* Align left behind the text */
    padding-left: 10%;
    z-index: 0; 
    opacity: 0.08; 
    pointer-events: none; 
}

/* Rest Overlay specific centering */
.rest-overlay .timer-wrapper {
    align-items: center;
    text-align: center;
}

.timer-wrapper { display: flex; flex-direction: column; align-items: flex-start; }
.huge-timer { font-size: 25vw; line-height: 1; font-weight: 700; color: #ef4444; }
.huge-timer-exec { font-size: 35vw; line-height: 1; font-weight: 900; color: #0f172a; letter-spacing: -0.05em; font-family: monospace; }
.timer-label { font-size: 4vw; font-weight: 700; color: #ef4444; margin-top: 1rem; letter-spacing: 0.2em; text-transform: uppercase; }

/* Bottom Bar */
.bottom-control-bar { position: absolute; bottom: 0; width: 100%; padding: 2rem 3rem; background-color: rgba(255,255,255,0.95); backdrop-filter: blur(8px); border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; box-sizing: border-box; }

.preview-label { font-size: 1rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem; }
.preview-name { font-size: 2rem; font-weight: 700; color: #cbd5e1; margin: 0; }
.instruction-text { font-size: 1.25rem; color: #94a3b8; }

.progress-text { font-size: 3rem; font-weight: 900; color: #f1f5f9; margin: 0; }
.progress-total { font-size: 1.5rem; color: #f1f5f9; }

/* Controls */
.controls-wrapper { position: absolute; left: 50%; transform: translateX(-50%); bottom: 2rem; }
.paused-overlay { position: absolute; inset: 0; z-index: 50; display: flex; align-items: center; justify-content: center; background-color: rgba(255,255,255,0.5); backdrop-filter: blur(4px); }
.paused-badge { background-color: black; color: white; padding: 1.5rem 3rem; border-radius: 9999px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
.paused-text { font-size: 2.25rem; font-weight: 900; letter-spacing: 0.1em; text-transform: uppercase; }

/* Training Header */
.session-tags { display: flex; gap: 0.5rem; }
.step-indicator { display: flex; align-items: center; gap: 0.75rem; }
.step-text { font-size: 0.875rem; color: #64748b; }
.progress-bar-container { margin-bottom: 2rem; }

/* Completed */
.success-icon-wrapper { width: 4rem; height: 4rem; background-color: #dcfce7; color: #16a34a; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; margin-bottom: 1.5rem; }
.success-check { font-size: 1.5rem; }

/* Animations */
@keyframes bounce { 
    0%, 100% { transform: translateY(-25%); animation-timing-function: cubic-bezier(0.8,0,1,1); }
    50% { transform: none; animation-timing-function: cubic-bezier(0,0,0.2,1); }
}
.animate-bounce { animation: bounce 1s infinite; }
@keyframes pulse { 50% { opacity: .5; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(1rem); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fadeIn 0.5s ease-out forwards; }
/* Tutorial Styles */
.tutorial-card { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 500px; }
.tutorial-vis-wrapper { 
    width: 300px; 
    height: 300px; 
    margin: 0 auto 1.5rem; 
    background: #f8fafc; 
    border-radius: 20px; 
    overflow: hidden; 
    border: 1px solid #e2e8f0;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}
.gesture-title-large { font-size: 2rem; font-weight: 800; color: #0f172a; margin: 0 0 0.5rem; }
.gesture-subtitle { font-size: 1.1rem; color: #64748b; font-weight: 500; }
.tutorial-progress { width: 100%; max-width: 300px; margin: 0 auto; }
.progress-bar-bg { width: 100%; height: 8px; background: #e2e8f0; border-radius: 99px; overflow: hidden; margin-bottom: 0.5rem; }
.progress-bar-fill { height: 100%; background: #2563eb; transition: width 0.3s ease; }
.progress-text { font-size: 0.875rem; color: #94a3b8; }
</style>
