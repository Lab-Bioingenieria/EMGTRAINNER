<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import DoctorEMGChart from '../../components/doctor/DoctorEMGChart.vue'
import DoctorGestureMonitor from '../../components/doctor/DoctorGestureMonitor.vue'
import DoctorAlerts from '../../components/doctor/DoctorAlerts.vue'
import {
  Activity, RotateCcw, Check, Copy, Wifi, WifiOff, AlertTriangle,
  Play, Pause, Square, Plus, UserCheck, Loader2, FlaskConical, FileText, Download
} from 'lucide-vue-next'
import { useSessionStore } from '../../stores/session'
import { ALL_GESTURES, API_BASE_URL } from '../../lib/constants'
import type { TrainingMode, Gesture } from '../../lib/constants'
import { demoSensors, demoForcedByEnv, setDemoSensors } from '../../lib/demo'

const store = useSessionStore()

/**
 * `localStage` controla SOLO las pantallas de configuracion del doctor.
 * En cuanto pulsa "Iniciar y Esperar" pasa a 'live' y a partir de ahi la
 * pantalla la manda `store.phase`, que es el estado compartido con el paciente.
 */
type LocalStage = 'mode' | 'gestures' | 'verify' | 'live'
const localStage = ref<LocalStage>('mode')

const codeCopied = ref(false)
const tempSelectedGestures = ref<Gesture[]>([])
const protocolName = ref('')
const repetitions = ref(3)
const restTime = ref(5)
const gestureDuration = ref(5)

const formattedTime = computed(() => {
  const seconds = store.sessionTime
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

/** Duración final: la que reportó el paciente, o el cronómetro del doctor. */
const formattedDuration = computed(() => {
  const seconds = store.durationSeconds || store.sessionTime
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

const activeSignals = computed(() => store.activeSignals)
const sensorsReady = computed(() => store.sensorsReady)
const phase = computed(() => store.phase)
const trainingMode = computed(() => store.trainingMode)
const linkReady = computed(() => store.isLinked && !!store.sessionCode)

/** Enciende la simulación de sensores y refresca el estado al instante. */
const enableDemoSensors = () => {
  setDemoSensors(true)
  store.refreshSensors()
}

const disableDemoSensors = () => {
  setDemoSensors(false)
  store.refreshSensors()
}

const copyCode = () => {
  if (!store.sessionCode) return
  navigator.clipboard.writeText(store.sessionCode)
  codeCopied.value = true
  setTimeout(() => (codeCopied.value = false), 2000)
}

const handleSelectMode = (mode: TrainingMode) => {
  store.setTrainingMode(mode)
  if (mode === 'LLC') {
    // En modo autonomo el orden lo decide el backend; se manda el catalogo completo.
    const shuffled = [...ALL_GESTURES].sort(() => Math.random() - 0.5)
    store.setSelectedGestures(shuffled)
    localStage.value = 'verify'
  } else {
    tempSelectedGestures.value = []
    localStage.value = 'gestures'
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

/** Confirma el protocolo: los gestos viajan al servidor y de ahi al paciente. */
const handleConfirmGestures = () => {
  store.setSelectedGestures([...tempSelectedGestures.value])
  store.setProtocolParams({
    protocolName: protocolName.value,
    repetitions: repetitions.value,
    restTime: restTime.value,
    gestureDuration: gestureDuration.value
  })
  localStage.value = 'verify'
}

const handleBackToMode = () => {
  store.setTrainingMode(null)
  tempSelectedGestures.value = []
  localStage.value = 'mode'
}

const handleEditProtocol = () => {
  if (store.trainingMode === 'TLC') {
    tempSelectedGestures.value = [...store.selectedGestures]
    localStage.value = 'gestures'
  } else {
    handleBackToMode()
  }
}

/** Publica el codigo. NO se regenera nada: es el mismo que ya se ve en pantalla. */
const handleStartWaiting = () => {
  store.startWaiting()
  localStage.value = 'live'
}

const handleNewSession = () => {
  store.resetSession()
  tempSelectedGestures.value = []
  protocolName.value = ''
  localStage.value = 'mode'
}

const handleCancelWaiting = () => {
  store.resetSession()
  localStage.value = 'verify'
}

// Timer Logic
let interval: number | null = null

onMounted(async () => {
  // Abre la sala y recibe el UNICO codigo de la sesion.
  try {
    await store.openDoctorSession()
  } catch {
    // El estado del enlace ya queda reflejado en store.linkStatus/linkError.
  }
  store.startSensorPolling()

  interval = window.setInterval(() => {
    if (store.phase === 'running') store.incrementTime()
  }, 1000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
  store.stopSensorPolling()
  store.closeLink()
})
</script>

<template>
  <div class="page-layout">
    <!-- ============ CONFIGURACION: seleccion de modo ============ -->
    <template v-if="localStage === 'mode'">
      <TopHeader title="Sesión Doctor" subtitle="Configurar protocolo de entrenamiento" />
      <div class="content">
        <div class="setup-container">
          <div v-if="store.linkStatus === 'error'" class="alert-message mb-section">
            <AlertTriangle class="icon-sm text-destructive" />
            <span>{{ store.linkError }} Verifique que el backend esté en ejecución.</span>
          </div>

          <div class="card bg-white mb-section">
            <h3 class="card-title mb-input">Nuevo Protocolo</h3>
            <div class="field-group">
              <label>Nombre del protocolo (opcional)</label>
              <input v-model="protocolName" placeholder="Ej: Rehabilitación inicial..." class="input" />
            </div>
          </div>

          <h2 class="section-title">Seleccionar Modo de Entrenamiento</h2>
          <div class="grid-modes">
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

    <!-- ============ CONFIGURACION: gestos del protocolo (TLC) ============ -->
    <template v-else-if="localStage === 'gestures'">
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
                 @click="toggleGesture(gesture)">
              <h3 class="gesture-name">{{ gesture.name }}</h3>
              <p class="gesture-sub">{{ gesture.nameEn }}</p>
            </div>
          </div>

          <div class="card bg-white mb-section">
            <h3 class="card-title mb-input">Parámetros</h3>
            <div class="grid-params">
              <div class="field-group">
                <label>Repeticiones del circuito</label>
                <input type="number" v-model.number="repetitions" min="1" max="10" class="input" />
              </div>
              <div class="field-group">
                <label>Duración por gesto (seg)</label>
                <input type="number" v-model.number="gestureDuration" min="1" max="60" class="input" />
              </div>
              <div class="field-group">
                <label>Tiempo de descanso (seg)</label>
                <input type="number" v-model.number="restTime" min="1" max="30" class="input" />
              </div>
            </div>
          </div>

          <div class="action-buttons">
            <button class="btn btn-ghost" @click="handleBackToMode">Cambiar modo</button>
            <button class="btn btn-primary" :disabled="tempSelectedGestures.length === 0" @click="handleConfirmGestures">
              Confirmar Protocolo
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- ============ CONFIGURACION: verificacion de señales ============ -->
    <template v-else-if="localStage === 'verify'">
      <TopHeader title="Sesión Doctor" subtitle="Verificar señales sEMG" />
      <div class="content">
        <div class="setup-container">
          <div class="card info-bar mb-section">
            <div class="info-left">
              <span class="badge info-badge">{{ trainingMode === 'TLC' ? 'Modo Guiado' : 'Modo Autónomo' }}</span>
              <span class="info-text">{{ store.selectedGestures.length }} gestos</span>
            </div>
            <div class="code-section">
              <span class="code-caption">Código de sesión</span>
              <code class="session-code">{{ store.sessionCode || '· · · · · ·' }}</code>
              <button class="btn-icon" :disabled="!linkReady" @click="copyCode">
                <Check v-if="codeCopied" class="icon-sm text-success" />
                <Copy v-else class="icon-sm" />
              </button>
            </div>
          </div>

          <div class="card signals-card mb-section">
            <div class="signals-header">
              <h3 class="card-title">Estado de Señales sEMG</h3>
              <div class="signals-header-right">
                <span v-if="demoSensors" class="demo-badge">MODO DEMO</span>
                <span class="status-badge" :class="sensorsReady ? 'bg-success' : 'bg-destructive'">
                  <Wifi v-if="sensorsReady" class="icon-xs mr-1" />
                  <WifiOff v-else class="icon-xs mr-1" />
                  {{ activeSignals }}/3 Activas
                </span>
              </div>
            </div>
            <div class="signals-grid">
              <div v-for="signal in store.emgSignals" :key="signal.id" class="signal-item" :class="signal.status">
                <div class="signal-dot"></div>
                <p class="signal-name">{{ signal.name }}</p>
              </div>
            </div>

            <!-- Sin hardware conectado: permite recorrer el flujo simulando los canales. -->
            <div v-if="!sensorsReady" class="alert-message alert-with-action">
              <div class="alert-text">
                <AlertTriangle class="icon-sm text-destructive" />
                <span>Se requieren 3 señales activas para iniciar. ¿No tiene los sensores conectados?</span>
              </div>
              <button class="btn btn-demo" @click="enableDemoSensors">
                <FlaskConical class="icon-sm mr-2" /> Usar modo demo
              </button>
            </div>

            <div v-else-if="demoSensors" class="demo-notice">
              <FlaskConical class="icon-sm" />
              <span>Señales simuladas — los datos de esta sesión no provienen del dispositivo.</span>
              <button v-if="!demoForcedByEnv" class="btn-link" @click="disableDemoSensors">Desactivar</button>
            </div>
          </div>

          <div v-if="!linkReady" class="alert-message mb-section">
            <AlertTriangle class="icon-sm text-destructive" />
            <span>{{ store.linkError || 'Conectando con el servidor de sesiones...' }}</span>
          </div>

          <div class="action-buttons">
            <button class="btn btn-ghost" @click="handleEditProtocol">Editar</button>
            <button class="btn btn-primary" :disabled="!sensorsReady || !linkReady" @click="handleStartWaiting">
              Iniciar y Esperar
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- ============ ESPERANDO CONEXION DEL PACIENTE ============ -->
    <!-- Solo se sale de aqui cuando el paciente entra con el codigo correcto. -->
    <template v-else-if="phase === 'waiting'">
      <TopHeader title="Sesión Doctor" subtitle="Esperando conexión..." />
      <div class="content layout-center">
        <div class="waiting-card">
          <div class="pulse-icon"><Wifi class="icon-lg text-primary" /></div>
          <h2 class="waiting-title">Esperando Conexión</h2>
          <p class="waiting-subtitle">Comparta este código con el paciente.</p>
          <div class="code-wrapper">
            <code class="code-big">{{ store.sessionCode }}</code>
          </div>
          <p class="waiting-hint">
            <Loader2 class="icon-sm spin" />
            La sesión continuará automáticamente cuando el paciente se conecte.
          </p>
          <button class="btn btn-outline" @click="handleCancelWaiting">Cancelar</button>
        </div>
      </div>
    </template>

    <!-- ============ PACIENTE CONECTADO, REVISANDO PROTOCOLOS ============ -->
    <!-- La pantalla de señales en tiempo real se habilita cuando el paciente
         pulsa "Iniciar sesión" en su lado. -->
    <template v-else-if="phase === 'connected'">
      <TopHeader title="Sesión Doctor" subtitle="Paciente conectado" />
      <div class="content layout-center">
        <div class="waiting-card">
          <div class="pulse-icon success"><UserCheck class="icon-lg text-success" /></div>
          <h2 class="waiting-title">Paciente conectado</h2>
          <p class="waiting-subtitle">
            {{ store.patientName || 'El paciente' }} está revisando los protocolos de inicio.
          </p>
          <p class="waiting-hint">
            <Loader2 class="icon-sm spin" />
            Esperando que confirme para habilitar el monitoreo en tiempo real.
          </p>
          <button class="btn btn-outline" @click="handleCancelWaiting">Cancelar sesión</button>
        </div>
      </div>
    </template>

    <!-- ============ SESION EN VIVO (señales sEMG en tiempo real) ============ -->
    <template v-else>
      <TopHeader
        title="Sesión Doctor"
        :subtitle="phase === 'ready' ? 'Paciente listo — puede iniciar'
          : phase === 'running' ? 'En curso'
          : phase === 'paused' ? 'En pausa'
          : 'Sesión finalizada'"
      />
      <div class="content">
        <div class="dashboard-container">
          <div class="control-bar mb-section">
            <div class="status-group">
              <span class="status-label" :class="'status-' + phase">{{ phase }}</span>
              <span class="timer-display">{{ formattedTime }}</span>
              <span class="patient-chip" :class="{ ready: store.patientReady }">
                <UserCheck class="icon-xs mr-1" />
                {{ store.patientReady ? 'Paciente listo' : 'Paciente conectado' }}
              </span>
              <span v-if="store.totalSteps > 0" class="progress-chip">
                Gesto {{ store.currentStep + 1 }} / {{ store.totalSteps }}
              </span>
              <code class="session-code">{{ store.sessionCode }}</code>
            </div>
            <div class="controls-group">
              <!-- Este botón habilita la pantalla de gestos del paciente. -->
              <button
                v-if="phase === 'ready'"
                class="btn btn-success"
                :disabled="!store.canStartSession"
                :title="!sensorsReady ? 'Se requieren 3 señales sEMG activas' : ''"
                @click="store.startSession()">
                <Play class="icon-sm mr-2" /> Iniciar
              </button>
              <template v-if="phase === 'running'">
                <button class="btn btn-outline" @click="store.pauseSession()"><Pause class="icon-sm mr-2" /> Pausar</button>
                <button class="btn btn-destructive" @click="store.finishSession()"><Square class="icon-sm mr-2" /> Finalizar</button>
              </template>
              <template v-if="phase === 'paused'">
                <button class="btn btn-success" @click="store.resumeSession()"><Play class="icon-sm mr-2" /> Continuar</button>
                <button class="btn btn-destructive" @click="store.finishSession()"><Square class="icon-sm mr-2" /> Finalizar</button>
              </template>
              <button v-if="phase === 'finished'" class="btn btn-primary" @click="handleNewSession">
                <Plus class="icon-sm mr-2" /> Nueva Sesión
              </button>
            </div>
          </div>

          <div v-if="phase === 'ready'" class="alert-info mb-section">
            <UserCheck class="icon-sm" />
            <span>El paciente confirmó los protocolos. Pulse «Iniciar» para habilitar su pantalla de gestos.</span>
          </div>

          <!-- RESUMEN DE RESULTADOS -->
          <div v-if="phase === 'finished'" class="card summary-card mb-section">
            <h3 class="card-title mb-input">Resultados de la sesión</h3>
            <div class="summary-grid">
              <div class="summary-item">
                <span class="summary-value">{{ store.patientName || '—' }}</span>
                <span class="summary-label">Paciente</span>
              </div>
              <div class="summary-item">
                <span class="summary-value">{{ store.completedSteps }}</span>
                <span class="summary-label">Gestos completados</span>
              </div>
              <div class="summary-item">
                <span class="summary-value">{{ formattedDuration }}</span>
                <span class="summary-label">Duración</span>
              </div>
              <div class="summary-item">
                <span class="summary-value">{{ trainingMode === 'TLC' ? 'Guiado' : 'Autónomo' }}</span>
                <span class="summary-label">Modo</span>
              </div>
            </div>

            <div v-if="store.csvFilename" class="csv-card">
              <div class="csv-icon"><FileText class="icon-sm" /></div>
              <div class="csv-info">
                <p class="csv-name">{{ store.csvFilename }}</p>
                <p class="csv-meta">Registro sEMG de la sesión</p>
              </div>
              <a :href="`${API_BASE_URL}/storage/sessions/${store.csvFilename}`"
                 download class="btn btn-outline btn-download">
                <Download class="icon-sm mr-2" /> Descargar CSV
              </a>
            </div>
            <p v-else class="csv-empty">
              No se generó archivo de datos: la sesión corrió sin sensores conectados.
            </p>

            <p class="storage-hint">
              El historial completo está en
              <router-link to="/storage" class="link">Almacenamiento → Historial CSV</router-link>.
            </p>
          </div>

          <div v-if="phase !== 'finished'" class="dashboard-grid">
            <div class="chart-area">
              <DoctorEMGChart :is-running="phase === 'running'" />
            </div>
            <div class="widgets-area">
              <!-- El nombre lo reporta el paciente. Indexar selectedGestures con
                   currentStep fallaba al pasar de la primera repetición. -->
              <DoctorGestureMonitor :gesture="store.currentGesture || '—'" />
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
.page-layout { display: flex; flex-direction: column; height: 100%; background: var(--bone-50); font-family: var(--font-sans); }
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

.mode-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; cursor: pointer; transition: all 0.2s; }
.mode-card:hover { border-color: #3b82f6; background-color: #f8fafc; transform: translateY(-2px); }
.mode-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem; }
.icon-circle { width: 40px; height: 40px; border-radius: 50%; background-color: #eff6ff; display: flex; align-items: center; justify-content: center; }
.mode-title { font-weight: 600; font-size: 1rem; color: #0f172a; margin: 0; }
.mode-subtitle { font-size: 0.75rem; color: #64748b; margin: 0; }
.mode-desc { font-size: 0.875rem; color: #64748b; line-height: 1.5; }

/* Gestures Grid */
.grid-gestures { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
@media(min-width: 768px) { .grid-gestures { grid-template-columns: repeat(4, 1fr); } }

.gesture-item { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.2s; }
.gesture-item:hover { background-color: #f8fafc; }
.gesture-item.selected { border-color: #3b82f6; background-color: #eff6ff; }
.gesture-name { font-size: 0.875rem; font-weight: 500; color: #0f172a; margin: 0; }
.gesture-sub { font-size: 0.75rem; color: #64748b; margin: 0; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.count-badge { background-color: #f1f5f9; color: #64748b; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 500; }

/* Params Grid */
.grid-params { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 768px) { .grid-params { grid-template-columns: repeat(3, 1fr); } }

/* Verification Bar */
.info-bar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; flex-wrap: wrap; gap: 0.75rem; }
.info-left { display: flex; align-items: center; gap: 1rem; }
.info-badge { background-color: #eff6ff; color: #1d4ed8; padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.875rem; font-weight: 500; }
.info-text { color: #64748b; font-size: 0.875rem; }
.code-section { display: flex; align-items: center; gap: 0.5rem; }
.code-caption { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
.session-code { font-family: monospace; font-weight: 700; background: #f1f5f9; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 1rem; letter-spacing: 0.1em; }

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
.alert-with-action { justify-content: space-between; flex-wrap: wrap; gap: 0.75rem; }
.alert-text { display: flex; align-items: center; gap: 0.5rem; }

/* Modo demo de sensores */
.signals-header-right { display: flex; align-items: center; gap: 0.5rem; }
.demo-badge { background-color: #fef3c7; color: #92400e; font-size: 0.6875rem; font-weight: 800; letter-spacing: 0.08em; padding: 0.25rem 0.5rem; border-radius: 4px; }
.btn-demo { background-color: #fff; border: 1px solid #fca5a5; color: #991b1b; font-weight: 600; white-space: nowrap; }
.btn-demo:hover { background-color: #fef2f2; }
.demo-notice { display: flex; align-items: center; gap: 0.5rem; margin-top: 1rem; padding: 0.75rem; border-radius: 6px; background-color: #fffbeb; border: 1px solid #fde68a; color: #92400e; font-size: 0.8125rem; }
.btn-link { margin-left: auto; background: none; border: none; color: #92400e; text-decoration: underline; cursor: pointer; font-size: 0.8125rem; font-weight: 600; }
.alert-info { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1rem; background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; color: #1e40af; font-size: 0.875rem; }

/* Waiting Screen */
.waiting-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 3rem; text-align: center; max-width: 28rem; width: 100%; }
.pulse-icon { width: 64px; height: 64px; background-color: #eff6ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; animation: pulse 2s infinite; }
.pulse-icon.success { background-color: #dcfce7; }
.waiting-title { font-size: 1.25rem; font-weight: 600; color: #0f172a; margin-bottom: 0.5rem; }
.waiting-subtitle { color: #64748b; margin-bottom: 1.5rem; }
.code-wrapper { margin-bottom: 1.5rem; }
.code-big { font-family: monospace; font-size: 2.5rem; letter-spacing: 0.2em; background: #f1f5f9; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 700; color: #0f172a; }
.waiting-hint { display: flex; align-items: center; justify-content: center; gap: 0.5rem; font-size: 0.8125rem; color: #94a3b8; margin-bottom: 1.5rem; }

/* Dashboard Running */
.control-bar { background: white; border-radius: 8px; border: 1px solid #e2e8f0; padding: 0.75rem 1.5rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05); flex-wrap: wrap; gap: 0.75rem; }
.status-group { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.status-label { text-transform: capitalize; padding: 0.25rem 0.75rem; border-radius: 4px; font-weight: 600; font-size: 0.875rem; }
.status-running { background-color: #dcfce7; color: #166534; }
.status-paused { background-color: #fef3c7; color: #92400e; }
.status-finished { background-color: #dbeafe; color: #1e40af; }
.status-connected { background-color: #f3e8ff; color: #6b21a8; }
.status-ready { background-color: #cffafe; color: #155e75; }
.timer-display { font-family: monospace; font-size: 1.125rem; font-weight: 600; color: #0f172a; }
.patient-chip { display: inline-flex; align-items: center; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.625rem; border-radius: 99px; background-color: #f1f5f9; color: #64748b; }
.patient-chip.ready { background-color: #dcfce7; color: #166534; }
.progress-chip { font-size: 0.75rem; font-weight: 600; color: #475569; background-color: #f1f5f9; padding: 0.25rem 0.625rem; border-radius: 99px; }
.controls-group { display: flex; gap: 0.5rem; }
.controls-group .btn:disabled { opacity: 0.6; cursor: not-allowed; }
.session-error { margin: -0.5rem 0 1rem; padding: 0.625rem 1rem; border-radius: 6px; background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; font-size: 0.875rem; }

/* Resumen de resultados */
.summary-card { padding: 1.5rem; }
.summary-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1.25rem; }
@media(min-width: 768px) { .summary-grid { grid-template-columns: repeat(4, 1fr); } }
.summary-item { background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 10px; padding: 1rem; display: flex; flex-direction: column; gap: 0.25rem; }
.summary-value { font-size: 1.25rem; font-weight: 800; color: #0f172a; font-variant-numeric: tabular-nums; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.summary-label { font-size: 0.6875rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.csv-card { display: flex; align-items: center; gap: 0.75rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.75rem; flex-wrap: wrap; }
.csv-icon { width: 2rem; height: 2rem; flex-shrink: 0; border-radius: 8px; background: #dcfce7; color: #16a34a; display: flex; align-items: center; justify-content: center; }
.csv-info { flex: 1; min-width: 0; }
.csv-name { font-size: 0.8125rem; font-weight: 600; color: #334155; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.csv-meta { font-size: 0.75rem; color: #94a3b8; margin: 0; }
.btn-download { text-decoration: none; }
.csv-empty { font-size: 0.8125rem; color: #94a3b8; margin: 0; padding: 0.75rem; background: #f8fafc; border-radius: 8px; }
.storage-hint { font-size: 0.75rem; color: #94a3b8; margin: 1rem 0 0; }
.link { color: #2563eb; text-decoration: underline; }

.dashboard-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 1024px) { .dashboard-grid { grid-template-columns: 2fr 1fr; } }
.widgets-area { display: flex; flex-direction: column; gap: 1.5rem; }

/* Buttons & Common */
.action-buttons { display: flex; gap: 0.75rem; }
.btn { padding: 0.5rem 1rem; border-radius: 6px; font-weight: 500; font-size: 0.875rem; cursor: pointer; border: none; transition: background 0.2s; display: inline-flex; align-items: center; justify-content: center; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:hover:not(:disabled) { background-color: #1e293b; }
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
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; }
</style>
