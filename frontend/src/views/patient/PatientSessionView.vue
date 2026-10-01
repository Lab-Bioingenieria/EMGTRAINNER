<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import TopHeader from '../../components/common/TopHeader.vue'
import PatientHandVisualization from '../../components/patient/PatientHandVisualization.vue'
import { ALL_GESTURES, API_BASE_URL } from '../../lib/constants'
import type { Gesture } from '../../lib/constants'
import { Wifi, ChevronRight, Maximize, CheckCircle2, AlertTriangle, Loader2, FlaskConical, FileText, Download } from 'lucide-vue-next'
import { useSessionStore } from '../../stores/session'
import { demoSensors, setDemoSensors } from '../../lib/demo'
import { EmgService } from '../../services/emg.service'

const router = useRouter()
const store = useSessionStore()

/**
 * Flujo del paciente supervisado:
 *   selection -> code -> protocols -> waiting-doctor -> training -> completed
 *
 * Los saltos entre `waiting-doctor`, `training` y `completed` los manda el
 * doctor a traves del estado compartido: el paciente nunca avanza solo.
 */
type Step = 'selection' | 'code' | 'protocols' | 'waiting-doctor' | 'training' | 'completed'
const step = ref<Step>('selection')

const sessionCode = ref('')
const patientName = ref('')
const codeError = ref('')
const connecting = ref(false)

const activeSignals = computed(() => store.activeSignals)
const sensorsReady = computed(() => store.sensorsReady)
const trainingMode = computed(() => store.trainingMode)

// --- Datos del entrenamiento (llegan del doctor) ---
const gestures = ref<Gesture[]>([])
const currentStep = ref(0)
const completedSteps = ref<number[]>([])

// --- Estado de ejecucion ---
const isExecuting = ref(false)
const isResting = ref(false)
const isCountingDown = ref(false)
const timer = ref(5)
const restTimer = ref(5)
const countdownTimer = ref(3)

const currentGesture = computed(() => gestures.value[currentStep.value] || null)
const nextGesture = computed(() => gestures.value[currentStep.value + 1] || null)
const isPausedByDoctor = computed(() => store.phase === 'paused')

// --- Captura de datos (CSV de la sesión) ---
const lastSession = ref<any>(null)
let captureStarted = false
let captureStopped = false
let sessionStartedAt = 0

const elapsedSeconds = () =>
  sessionStartedAt ? Math.round((Date.now() - sessionStartedAt) / 1000) : 0

/** Arranca la grabación sEMG etiquetada con el nombre del paciente. */
const startCapture = async () => {
  if (captureStarted) return
  captureStarted = true
  captureStopped = false
  sessionStartedAt = Date.now()
  try {
    await EmgService.setSessionInfo(patientName.value || 'Anonimo')
    await EmgService.startSession(store.trainingMode || '')
  } catch (e) {
    console.error('No se pudo iniciar la captura sEMG', e)
  }
}

/**
 * Cierra la grabación, recupera el CSV y lo adjunta a la sesión para que el
 * doctor también pueda descargarlo. Es idempotente: la llaman tanto el fin
 * natural del circuito como el botón «Finalizar» del doctor.
 */
const stopCapture = async () => {
  if (!captureStarted || captureStopped) return
  captureStopped = true
  const duration = elapsedSeconds()
  try {
    await EmgService.stopSession()
    // Pequeña espera para que el archivo termine de escribirse.
    await new Promise(resolve => setTimeout(resolve, 500))
    lastSession.value = await EmgService.getLatestSession()
  } catch (e) {
    console.error('No se pudo cerrar la captura sEMG', e)
  }
  store.reportResult(lastSession.value?.filename || '', duration, completedSteps.value.length)
}

/** Simula los 3 canales cuando no hay hardware conectado. */
const enableDemoSensors = () => {
  setDemoSensors(true)
  store.refreshSensors()
}

const selectMode = (mode: 'supervised' | 'free') => {
  if (mode === 'free') {
    router.push('/patient/free')
  } else {
    codeError.value = ''
    step.value = 'code'
  }
}

/**
 * Valida el codigo contra la sesion del doctor. Si no coincide, el paciente
 * se queda en esta pantalla y se le pide un codigo correcto.
 */
const connectSession = async () => {
  codeError.value = ''
  connecting.value = true
  try {
    await store.connectAsPatient(sessionCode.value, patientName.value)
    step.value = 'protocols'
    currentStep.value = 0
    completedSteps.value = []
  } catch {
    codeError.value = store.linkError || 'Código incorrecto. Solicite el código correcto al terapeuta.'
    store.closeLink()
  } finally {
    connecting.value = false
  }
}

/** El paciente confirma los protocolos: esto habilita el botón «Iniciar» del doctor. */
const confirmProtocols = () => {
  store.markPatientReady()
  step.value = 'waiting-doctor'
}

const enterFullscreen = () => {
  const elem = document.documentElement
  if (elem.requestFullscreen) {
    elem.requestFullscreen().catch((err) => console.warn('Error attempting to enable fullscreen:', err))
  }
}

const exitFullscreen = () => {
  if (document.fullscreenElement && document.exitFullscreen) {
    document.exitFullscreen().catch(() => undefined)
  }
}

// ---------------------------------------------------------------- gestos LLC

const fetchNextGestureSuggestion = async (): Promise<string | null> => {
  try {
    const response = await fetch(`/v1/learning/next-gesture/${encodeURIComponent(patientName.value || 'Guest')}`)
    if (response.ok) {
      const data = await response.json()
      return data.next_gesture
    }
  } catch (e) {
    console.error('Error fetching next gesture:', e)
  }
  return null
}

const getNextGesture = async (): Promise<Gesture> => {
  const nextName = await fetchNextGestureSuggestion()
  if (!nextName) {
    const last = gestures.value.length > 0 ? gestures.value[gestures.value.length - 1] : null
    const candidates = ALL_GESTURES.filter(g => g.name !== last?.name)
    return candidates[Math.floor(Math.random() * candidates.length)]
  }
  return ALL_GESTURES.find(g => g.name === nextName) || ALL_GESTURES[0]
}

/** Construye la lista de gestos exactamente como la definió el doctor. */
const buildGestureList = async () => {
  const protocol = store.selectedGestures.length > 0 ? store.selectedGestures : ALL_GESTURES.slice(0, 4)

  if (store.trainingMode === 'LLC') {
    gestures.value = [await getNextGesture(), await getNextGesture()]
    return
  }

  let expanded: Gesture[] = []
  const reps = Math.max(1, store.repetitions || 1)
  for (let i = 0; i < reps; i++) expanded = expanded.concat(protocol)
  gestures.value = expanded
}

// -------------------------------------------------------------- temporizador

let intervalId: number | undefined

const stopTimer = () => {
  if (intervalId !== undefined) {
    clearInterval(intervalId)
    intervalId = undefined
  }
}

const runTimer = (phase: 'countdown' | 'execution' | 'rest') => {
  stopTimer()
  if (isPausedByDoctor.value) return
  intervalId = window.setInterval(() => {
    if (phase === 'countdown') {
      countdownTimer.value--
      if (countdownTimer.value <= 0) {
        stopTimer()
        isCountingDown.value = false
        startExecution()
      }
    } else if (phase === 'execution') {
      timer.value--
      if (timer.value <= 0) finishStep()
    } else {
      restTimer.value--
      if (restTimer.value <= 0) endRest()
    }
  }, 1000)
}

const startCountdown = () => {
  isCountingDown.value = true
  isResting.value = false
  isExecuting.value = false
  countdownTimer.value = 3
  runTimer('countdown')
}

const startExecution = () => {
  isExecuting.value = true
  isResting.value = false
  timer.value = store.gestureDuration || 5

  const name = gestures.value[currentStep.value]?.name || ''
  // Etiqueta con la que se guardará este tramo en el CSV.
  EmgService.setMovementLabel(name).catch(() => undefined)
  // El doctor muestra este nombre: no puede deducirlo del índice, porque en TLC
  // la lista del paciente es el protocolo repetido N veces.
  store.reportStep(currentStep.value, name, gestures.value.length, completedSteps.value.length)

  runTimer('execution')
}

const finishStep = async () => {
  stopTimer()
  isExecuting.value = false
  if (!completedSteps.value.includes(currentStep.value)) {
    completedSteps.value.push(currentStep.value)
  }

  if (store.trainingMode === 'LLC') {
    gestures.value.push(await getNextGesture())
  } else if (currentStep.value >= gestures.value.length - 1) {
    // Fin del circuito: se guarda el CSV y se cierra la sesión en ambos lados.
    await stopCapture()
    store.finishSession(elapsedSeconds())
    return
  }

  startRest()
}

const startRest = () => {
  isResting.value = true
  restTimer.value = store.restTime || 5
  EmgService.setMovementLabel('Rest').catch(() => undefined)
  runTimer('rest')
}

const endRest = () => {
  stopTimer()
  isResting.value = false
  currentStep.value++
  startExecution()
}

/** Reanuda la fase en curso tras una pausa del doctor. */
const resumeCurrentPhase = () => {
  if (isCountingDown.value) runTimer('countdown')
  else if (isResting.value) runTimer('rest')
  else if (isExecuting.value) runTimer('execution')
}

// ------------------------------------------------------- reacciones al doctor

watch(() => store.phase, async (phase, previous) => {
  if (phase === 'running' && previous !== 'paused') {
    // El doctor pulsó «Iniciar»: se habilita la pantalla de gestos.
    await buildGestureList()
    currentStep.value = 0
    completedSteps.value = []
    await startCapture()
    step.value = 'training'
    enterFullscreen()
    startCountdown()
  } else if (phase === 'running' && previous === 'paused') {
    resumeCurrentPhase()
  } else if (phase === 'paused') {
    stopTimer()
    EmgService.setMovementLabel('Pause').catch(() => undefined)
  } else if (phase === 'finished') {
    // Cubre tanto el fin natural del circuito como el botón «Finalizar» del doctor.
    stopTimer()
    await stopCapture()
    exitFullscreen()
    step.value = 'completed'
  } else if (phase === 'waiting' && step.value !== 'selection' && step.value !== 'code') {
    // El doctor reinició la sesión o se cayó la conexión.
    stopTimer()
    exitFullscreen()
    step.value = 'code'
    codeError.value = 'La sesión fue reiniciada por el terapeuta.'
  }
})

const reset = () => {
  stopTimer()
  store.closeLink()
  step.value = 'selection'
  sessionCode.value = ''
  codeError.value = ''
  completedSteps.value = []
  gestures.value = []
  isResting.value = false
  isCountingDown.value = false
  isExecuting.value = false
  lastSession.value = null
  captureStarted = false
  captureStopped = false
  sessionStartedAt = 0
}

const formatDuration = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

onMounted(() => store.startSensorPolling())

onUnmounted(() => {
  stopTimer()
  store.stopSensorPolling()
  store.closeLink()
})
</script>

<template>
  <div class="page-layout">
    <TopHeader crumb="MÓDULO · SESIÓN PACIENTE" title="Sesión de Entrenamiento" />

    <div class="content flex-center-col">
      <!-- SELECCIÓN DE MODO -->
      <div v-if="step === 'selection'" class="container-sm">
        <div class="header-center">
          <h1 class="title-main">Iniciar Nueva Sesión</h1>
          <p class="subtitle-main">Seleccione el modo de operación para comenzar</p>
        </div>

        <div class="grid-2 gap-cards">
          <div class="card hoverable-card p-card" @click="selectMode('supervised')">
            <div class="card-header-row">
              <div class="icon-circle bg-blue-light text-blue"><Wifi class="icon-md" /></div>
              <div>
                <h3 class="card-title-lg">Sesión Supervisada</h3>
                <p class="text-xs text-muted">Requiere código de médico</p>
              </div>
            </div>
            <p class="text-desc">Conéctese con su terapeuta para una sesión guiada en tiempo real.</p>
            <div class="text-right"><ChevronRight class="icon-md text-slate-300" /></div>
          </div>

          <div class="card hoverable-card p-card" @click="selectMode('free')">
            <div class="card-header-row">
              <div class="icon-circle bg-indigo-light text-indigo"><span class="emoji-md">👤</span></div>
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

      <!-- CÓDIGO DE SESIÓN -->
      <div v-else-if="step === 'code'" class="container-xs">
        <div class="card p-large">
          <div class="header-center mb-6">
            <h2 class="title-section">Código de Sesión</h2>
            <p class="subtitle-text">Ingrese el código de 6 dígitos proporcionado por su terapeuta</p>
          </div>

          <div class="mb-4">
            <input
              v-model="sessionCode"
              maxlength="6"
              inputmode="numeric"
              placeholder="000000"
              class="input-code"
              :class="{ 'input-error': !!codeError }"
              @input="codeError = ''"
              @keyup.enter="sessionCode.length === 6 && sensorsReady && connectSession()"
            />
          </div>

          <div class="mb-6">
            <label class="field-label">Su nombre (opcional)</label>
            <input v-model="patientName" placeholder="Nombre del paciente" class="input-text" />
          </div>

          <!-- Código incorrecto: no se avanza en la plataforma -->
          <div v-if="codeError" class="error-box mb-6">
            <AlertTriangle class="icon-sm" />
            <span>{{ codeError }}</span>
          </div>

          <div class="sensor-status-box mb-6">
            <div class="status-header mb-4">
              <span class="status-label">Estado de Sensores</span>
              <div class="status-header-right">
                <span v-if="demoSensors" class="demo-badge">DEMO</span>
                <span class="badge" :class="sensorsReady ? 'badge-success' : 'badge-error'">
                  {{ sensorsReady ? 'Listo' : 'Verificar' }}
                </span>
              </div>
            </div>
            <div class="sensor-indicators">
              <div v-for="s in store.emgSignals" :key="s.id" class="sensor-item">
                <div class="sensor-dot" :class="s.status === 'active' ? 'bg-green' : 'bg-red'"></div>
                <span class="sensor-name">CH{{ s.id }}</span>
              </div>
            </div>
            <!-- Sin hardware conectado -->
            <button v-if="!sensorsReady" class="btn-demo-inline" @click="enableDemoSensors">
              <FlaskConical class="icon-sm" /> Sin sensores — usar modo demo
            </button>
          </div>

          <div class="actions-row">
            <button class="btn btn-outline flex-1" @click="reset">Cancelar</button>
            <button
              class="btn btn-primary flex-1"
              :disabled="sessionCode.length !== 6 || !sensorsReady || connecting"
              @click="connectSession">
              {{ connecting ? 'Validando...' : 'Conectar' }}
            </button>
          </div>
        </div>
      </div>

      <!-- PROTOCOLOS DE INICIO -->
      <div v-else-if="step === 'protocols'" class="container-sm">
        <div class="card p-large text-center">
          <div class="mb-6">
            <h2 class="title-2xl mb-2">Protocolos de Inicio</h2>
            <p class="subtitle-text">Por favor confirme los siguientes pasos antes de comenzar</p>
          </div>

          <div class="session-summary mb-8">
            <span class="badge badge-info">{{ trainingMode === 'TLC' ? 'Modo Guiado' : 'Modo Autónomo' }}</span>
            <span class="summary-text">{{ store.selectedGestures.length }} gestos · {{ store.gestureDuration }}s por gesto</span>
          </div>

          <div class="protocols-grid mb-8">
            <div class="protocol-card">
              <div class="protocol-icon bg-blue-light text-blue"><span class="emoji-lg">🧴</span></div>
              <h3 class="protocol-title">Limpieza</h3>
              <p class="protocol-desc">Limpiar la piel con alcohol para mejorar la señal.</p>
            </div>
            <div class="protocol-card">
              <div class="protocol-icon bg-indigo-light text-indigo"><span class="emoji-lg">🧠</span></div>
              <h3 class="protocol-title">Concentración</h3>
              <p class="protocol-desc">Mantenga máxima atención durante los ejercicios.</p>
            </div>
            <div class="protocol-card">
              <div class="protocol-icon bg-purple-light text-purple"><Maximize class="icon-md" /></div>
              <h3 class="protocol-title">Pantalla Completa</h3>
              <p class="protocol-desc">La sesión se mostrará en pantalla completa.</p>
            </div>
          </div>

          <button class="btn btn-primary w-full py-large flex-center shadow-hover" @click="confirmProtocols">
            Entendido, Iniciar Sesión <CheckCircle2 class="icon-sm ml-2" />
          </button>
        </div>
      </div>

      <!-- ESPERANDO AL DOCTOR -->
      <div v-else-if="step === 'waiting-doctor'" class="container-xs">
        <div class="card p-extra text-center">
          <div class="pulse-circle"><Loader2 class="icon-lg text-blue spin" /></div>
          <h2 class="title-2xl mb-2">Listo para comenzar</h2>
          <p class="subtitle-text mb-8">
            Su terapeuta iniciará la sesión en un momento. No cierre esta ventana.
          </p>
          <div class="code-pill">Sesión {{ store.sessionCode }}</div>
        </div>
      </div>

      <!-- ENTRENAMIENTO -->
      <div v-else-if="step === 'training'" class="fullscreen-overlay">
        <div v-if="isCountingDown" class="countdown-container animate-fade-in">
          <p v-if="currentStep === 0" class="countdown-label">Estamos listos para comenzar</p>
          <div class="countdown-number animate-bounce">{{ countdownTimer }}</div>
        </div>

        <div v-else class="execution-container animate-slide-up">
          <div v-if="isResting" class="rest-overlay-centered">
            <div class="timer-wrapper">
              <div class="timer-huge-rest">{{ restTimer }}</div>
              <p class="timer-label">DESCANSO</p>
            </div>
          </div>

          <div v-else class="top-timer-container">
            <div class="timer-wrapper"><div class="timer-huge-exec">{{ timer }}</div></div>
          </div>

          <div class="main-content">
            <div class="gesture-display">
              <h2 class="gesture-title-main">{{ isResting ? nextGesture?.name : currentGesture?.name }}</h2>
              <p class="gesture-subtitle-main">{{ isResting ? nextGesture?.nameEn : currentGesture?.nameEn }}</p>
            </div>
            <div class="visualization-box">
              <PatientHandVisualization
                :gesture="(isResting ? nextGesture?.name : currentGesture?.name) || ''"
                :is-active="!isResting" />
            </div>
          </div>

          <div class="bottom-bar">
            <div v-if="!isResting && nextGesture" class="next-gesture-info">
              <p class="next-label">Siguiente Movimiento</p>
              <div class="next-content"><h3 class="next-name">{{ nextGesture.name }}</h3></div>
            </div>
            <div v-else-if="isResting"><p class="breathing-text">Respire profundo...</p></div>

            <div class="progress-info">
              <p class="progress-number">
                {{ currentStep + 1 }}
                <span v-if="trainingMode === 'TLC'" class="progress-total">/{{ gestures.length }}</span>
                <span v-else class="progress-total">/ ∞</span>
              </p>
            </div>
          </div>

          <!-- Pausa controlada por el doctor -->
          <div v-if="isPausedByDoctor" class="doctor-pause-overlay">
            <div class="doctor-pause-badge">
              <p class="pause-title">Sesión en pausa</p>
              <p class="pause-sub">Su terapeuta reanudará la sesión</p>
            </div>
          </div>
        </div>
      </div>

      <!-- COMPLETADA — RESUMEN DE RESULTADOS -->
      <div v-else class="container-xs">
        <div class="card p-extra text-center">
          <div class="success-circle"><span class="check-mark">✓</span></div>
          <h2 class="title-2xl mb-3">Sesión Completada</h2>
          <p class="subtitle-text mb-6">Resumen de su sesión de entrenamiento.</p>

          <div class="result-grid mb-6">
            <div class="result-item">
              <span class="result-value">{{ completedSteps.length }}</span>
              <span class="result-label">Gestos completados</span>
            </div>
            <div class="result-item">
              <span class="result-value">{{ formatDuration(store.durationSeconds || elapsedSeconds()) }}</span>
              <span class="result-label">Duración</span>
            </div>
          </div>

          <!-- Archivo de la sesión -->
          <div v-if="lastSession" class="csv-card mb-6">
            <div class="csv-icon"><FileText class="icon-sm" /></div>
            <div class="csv-info">
              <p class="csv-name">{{ lastSession.filename }}</p>
              <p class="csv-meta">{{ (lastSession.size_bytes / 1024).toFixed(1) }} KB</p>
            </div>
            <a :href="`${API_BASE_URL}/storage/sessions/${lastSession.filename}`"
               download class="csv-download" title="Descargar CSV">
              <Download class="icon-sm" />
            </a>
          </div>
          <p v-else class="csv-empty mb-6">
            No se generó archivo de datos (sesión sin sensores conectados).
          </p>

          <p class="storage-hint mb-6">
            Todas las sesiones quedan en <strong>Almacenamiento → Historial CSV</strong>.
          </p>

          <button class="btn btn-outline w-full" @click="reset">Volver al Inicio</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Standard Layout */
.page-layout { display: flex; flex-direction: column; height: 100vh; background: var(--bone-50); font-family: var(--font-sans); }
.content { flex: 1; overflow: auto; padding: 2rem; display: flex; flex-direction: column; }
.flex-center-col { align-items: center; }

/* Containers */
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
.text-xs { font-size: 0.75rem; }
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
.icon-lg { width: 36px; height: 36px; }
.emoji-md { font-size: 1.25rem; }
.emoji-lg { font-size: 1.5rem; }

.bg-blue-light { background-color: #eff6ff; } .text-blue { color: #2563eb; }
.bg-indigo-light { background-color: #eef2ff; } .text-indigo { color: #4f46e5; }
.bg-purple-light { background-color: #f3e8ff; } .text-purple { color: #9333ea; }
.bg-green { background-color: #22c55e; }
.bg-red { background-color: #ef4444; }
.text-slate-300 { color: #cbd5e1; }

.success-circle { width: 4rem; height: 4rem; background-color: #dcfce7; color: #16a34a; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; }
.check-mark { font-size: 1.5rem; }
.pulse-circle { width: 4rem; height: 4rem; background-color: #eff6ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; }
.code-pill { display: inline-block; font-family: monospace; letter-spacing: 0.15em; font-weight: 700; background: #f1f5f9; color: #475569; padding: 0.5rem 1rem; border-radius: 8px; }

/* Code Input */
.input-code {
  text-align: center; font-family: 'Roboto', monospace; font-size: 2rem; padding: 1rem; width: 100%;
  border: 2px solid #e2e8f0; border-radius: 12px; letter-spacing: 0.25em; font-weight: 700; color: #0f172a;
  transition: all 0.2s; box-sizing: border-box;
}
.input-code:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }
.input-code.input-error { border-color: #ef4444; box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1); }
.field-label { display: block; font-size: 0.875rem; font-weight: 500; color: #475569; margin-bottom: 0.375rem; }
.input-text { width: 100%; padding: 0.625rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; box-sizing: border-box; }
.input-text:focus { border-color: #3b82f6; outline: none; }

.error-box { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1rem; background-color: #fee2e2; border: 1px solid #fecaca; border-radius: 8px; color: #b91c1c; font-size: 0.875rem; }

/* Session summary */
.session-summary { display: flex; align-items: center; justify-content: center; gap: 0.75rem; }
.summary-text { font-size: 0.875rem; color: #64748b; }
.badge-info { background-color: #eff6ff; color: #1d4ed8; }

.input-name {
    width: 100%; padding: 0.75rem 1rem; font-size: 1rem; box-sizing: border-box;
    border: 2px solid #e2e8f0; border-radius: 12px; color: #0f172a; transition: all 0.2s;
}
.input-name:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }

/* Sensor Status Box */
.sensor-status-box { background-color: #f8fafc; border-radius: 0.5rem; padding: 1rem; border: 1px solid #f1f5f9; }
.status-header { display: flex; justify-content: space-between; align-items: center; }
.status-label { font-size: 0.875rem; font-weight: 500; color: #334155; }
.sensor-indicators { display: flex; justify-content: center; gap: 1rem; }
.sensor-item { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; }
.sensor-dot { width: 0.75rem; height: 0.75rem; border-radius: 50%; }
.sensor-name { font-size: 0.75rem; color: #94a3b8; font-family: monospace; }
.badge { display: inline-flex; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.badge-success { background-color: #dcfce7; color: #16a34a; }
.badge-error { background-color: #fee2e2; color: #dc2626; }

/* Resumen de resultados */
.result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.result-item { background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 10px; padding: 1rem; display: flex; flex-direction: column; gap: 0.25rem; }
.result-value { font-size: 1.5rem; font-weight: 800; color: #0f172a; font-variant-numeric: tabular-nums; }
.result-label { font-size: 0.75rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.csv-card { display: flex; align-items: center; gap: 0.75rem; text-align: left; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.75rem; }
.csv-icon { width: 2rem; height: 2rem; flex-shrink: 0; border-radius: 8px; background: #dcfce7; color: #16a34a; display: flex; align-items: center; justify-content: center; }
.csv-info { flex: 1; min-width: 0; }
.csv-name { font-size: 0.8125rem; font-weight: 600; color: #334155; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.csv-meta { font-size: 0.75rem; color: #94a3b8; margin: 0; }
.csv-download { width: 2rem; height: 2rem; flex-shrink: 0; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #475569; }
.csv-download:hover { background: #e2e8f0; color: #0f172a; }
.csv-empty { font-size: 0.8125rem; color: #94a3b8; margin: 0; }
.storage-hint { font-size: 0.75rem; color: #94a3b8; margin: 0; }

/* Modo demo de sensores */
.status-header-right { display: flex; align-items: center; gap: 0.5rem; }
.demo-badge { background-color: #fef3c7; color: #92400e; font-size: 0.625rem; font-weight: 800; letter-spacing: 0.08em; padding: 0.2rem 0.45rem; border-radius: 4px; }
.btn-demo-inline {
  display: flex; align-items: center; justify-content: center; gap: 0.4rem; width: 100%;
  margin-top: 1rem; padding: 0.5rem; border-radius: 8px; cursor: pointer;
  background: #fffbeb; border: 1px solid #fde68a; color: #92400e; font-size: 0.8125rem; font-weight: 600;
}
.btn-demo-inline:hover { background: #fef3c7; }

/* Buttons */
.btn { padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:active { transform: scale(0.98); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-outline:hover { background-color: #f8fafc; }
.py-large { padding-top: 1rem; padding-bottom: 1rem; font-size: 1.125rem; }
.flex-1 { flex: 1; }
.w-full { width: 100%; }
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

.rest-overlay-centered { position: absolute; inset: 0; z-index: 20; background-color: white; display: flex; align-items: center; justify-content: center; }
.top-timer-container { position: absolute; top: 3rem; left: 0; right: 0; display: flex; justify-content: center; z-index: 0; }
.timer-wrapper { display: flex; flex-direction: column; align-items: center; text-align: center; }
.timer-huge-rest { font-size: 8rem; line-height: 1; font-weight: 700; color: #ef4444; }
.timer-label { font-size: 2.25rem; font-weight: 700; color: #ef4444; margin-top: 0.5rem; letter-spacing: 0.1em; }
.timer-huge-exec { font-size: 12rem; line-height: 1; font-weight: 900; color: #2563eb; font-variant-numeric: tabular-nums; }

.main-content { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; z-index: 10; }
.gesture-display { text-align: center; margin-bottom: 3rem; }
.gesture-title-main { font-size: 6rem; line-height: 1.1; font-weight: 900; color: #0f172a; letter-spacing: -0.02em; margin-bottom: 0.5rem; }
.gesture-subtitle-main { font-size: 2.25rem; color: #94a3b8; font-weight: 300; }

.visualization-box { width: 300px; height: 300px; transition: opacity 0.5s; }

.bottom-bar { position: absolute; bottom: 0; width: 100%; padding: 2rem; background-color: rgba(255,255,255,0.9); backdrop-filter: blur(4px); border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: flex-end; box-sizing: border-box; z-index: 30; }
.next-label { font-size: 1.25rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem; }
.next-name { font-size: 3rem; font-weight: 700; color: #cbd5e1; margin: 0; }
.breathing-text { font-size: 1.25rem; color: #94a3b8; }
.progress-number { font-size: 3.75rem; font-weight: 900; color: #f1f5f9; margin: 0; }
.progress-total { font-size: 2.25rem; color: #f1f5f9; }
.flex-center { display: flex; align-items: center; justify-content: center; }

/* Pausa del doctor */
.doctor-pause-overlay { position: absolute; inset: 0; z-index: 60; display: flex; align-items: center; justify-content: center; background-color: rgba(255,255,255,0.75); backdrop-filter: blur(6px); }
.doctor-pause-badge { background-color: #0f172a; color: white; padding: 2rem 3rem; border-radius: 1.5rem; text-align: center; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
.pause-title { font-size: 2.25rem; font-weight: 900; letter-spacing: 0.05em; margin: 0 0 0.5rem; }
.pause-sub { font-size: 1rem; color: #cbd5e1; margin: 0; }

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
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; }
</style>
