<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import EmgSerialPlotter from '../../components/common/EmgSerialPlotter.vue'
import MirrorHandVisualization from '../../components/patient/MirrorHandVisualization.vue'
import { useSessionStore } from '../../stores/session'
import { demoSensors, demoForcedByEnv, setDemoSensors } from '../../lib/demo'
import { buildAuthenticatedWebSocketUrl } from '../../lib/websocket'
import {
  HandMirrorService,
  STUDY_MOVEMENTS,
  type CalibrationGesture,
  type MirrorCalibrationStatus,
  type MirrorGestureStatus,
  type MirrorStudySession,
  type MirrorStudyStatus,
  type StudyMovement,
} from '../../services/hand-mirror.service'
import { AlertTriangle, Play, Square, FlaskConical, SlidersHorizontal, RotateCcw, ClipboardList } from 'lucide-vue-next'

/**
 * "Espejo en Tiempo Real": a pedido del tutor, un apartado aparte del
 * protocolo de gestos (CE-xx / Entrenamiento Libre). Acá no se reconoce ni
 * se ejecuta un gesto predefinido — la mano (física, si se activa, y la
 * vista previa en pantalla siempre) sigue de forma continua la amplitud
 * cruda que están mandando los sensores en este instante.
 */

// --- Sensores: misma fuente que Sesión Doctor / Sesión Paciente / Entrenamiento Libre ---
const store = useSessionStore()
const sensorsReady = computed(() => store.sensorsReady)
const emgSignals = computed(() => store.emgSignals)

const enableDemoSensors = () => {
  setDemoSensors(true)
  store.refreshSensors()
}

const disableDemoSensors = () => {
  setDemoSensors(false)
  store.refreshSensors()
}

// --- Mano física: arranca/detiene el lazo continuo del backend -------------
const mirrorActive = ref(false)
const busy = ref(false)
const mirrorError = ref('')
const showConfirm = ref(false)

// --- Estado del backend (sondeo único): mano física, vista previa y calibración ---
// El backend es la única fuente de verdad del valor calibrado; acá solo se muestra.
const activation = ref(0)          // cierre 0..1 de la vista previa (suavizado)
const previewConnected = ref(false) // llegan muestras recientes de los sensores
const channelLevels = ref<number[]>([])

const emptyCalibration = (): MirrorCalibrationStatus => ({
  state: 'idle', phase: null, step: 0, steps: 0, channel: null,
  gesture: null, seconds_left: 0, total_seconds: 0, message: '', error: null,
  running: false, calibrated: false, channels: [],
})
const calibration = ref<MirrorCalibrationStatus>(emptyCalibration())
const monitoring = ref(false)      // el backend mantiene el streaming encendido para esta pantalla
const emptyStudy = (): MirrorStudyStatus => ({
  state: 'idle', phase: null, step: 0, steps: 0, movement: null, rep: 0, reps: 0,
  seconds_left: 0, total_seconds: 0, elapsed: 0, duration: 0, message: '',
  error: null, file: null, rows: 0, running: false,
})
const study = ref<MirrorStudyStatus>(emptyStudy())
const emptyGesture = (): MirrorGestureStatus => ({ available: false, calibrated: false, label: null, confidence: 0 })
// Movimiento detectado por el clasificador entrenado con las sesiones del protocolo: SOLO
// informativo, se muestra junto a la vista previa pero no cambia el cierre proporcional de
// la mano (ver `claude/clasificador-de-movimientos.md`: con una persona nueva acierta poco
// más que "asumir reposo", así que se muestra como una pista, no como un hecho).
const gesture = ref<MirrorGestureStatus>(emptyGesture())

const STATUS_POLL_MS = 200
let statusPollId: number | null = null
let pollingInFlight = false

// Monitor: mantiene encendido el streaming (sin grabar) mientras la pantalla esta abierta,
// para que la vista previa y el grafico funcionen sin iniciar una sesion. Se renueva con
// cada sondeo de estado y el backend lo apaga solo si esta pantalla deja de sondear.
const MONITOR_RETRY_MS = 3000
let monitorPollId: number | null = null
async function ensureMonitor() {
  if (monitoring.value || demoSensors.value || !sensorsReady.value) return
  try {
    await HandMirrorService.startMonitor()
  } catch {
    /* sensor no conectado todavia: se reintenta */
  }
}

async function refreshMirrorStatus() {
  if (pollingInFlight) return
  pollingInFlight = true
  try {
    const status = await HandMirrorService.status()
    mirrorActive.value = status.active
    previewConnected.value = status.signal
    channelLevels.value = status.channels
    calibration.value = status.calibration
    monitoring.value = status.monitoring
    gesture.value = status.gesture
    const wasRunning = study.value.running
    study.value = status.study
    if (wasRunning && !status.study.running) loadStudySessions()  // termino: refrescar la lista
    const target = status.signal ? status.live : 0
    activation.value += (target - activation.value) * 0.5
  } catch {
    /* estado desconocido: se reintenta en el siguiente sondeo */
    previewConnected.value = false
  } finally {
    pollingInFlight = false
  }
}

// --- Calibración: reposo + contracción fuerte de cada sensor (lo guía el backend) ---
const calibBusy = ref(false)
const calibError = ref('')

const canCalibrate = computed(
  () => !calibBusy.value && !mirrorActive.value && !calibration.value.running && !study.value.running && !demoSensors.value && sensorsReady.value
)

const calibProgress = computed(() => {
  const c = calibration.value
  if (!c.total_seconds) return 0
  return Math.max(0, Math.min(100, (1 - c.seconds_left / c.total_seconds) * 100))
})

async function runCalibrationAction(action: () => Promise<unknown>) {
  calibBusy.value = true
  calibError.value = ''
  try {
    await action()
    await refreshMirrorStatus()
  } catch (e: any) {
    calibError.value = e.message || 'No se pudo completar la operación de calibración'
  } finally {
    calibBusy.value = false
  }
}

// --- Estudio de calibración por dedo: guarda cada sesión para entrenar el modelo ---
const studyName = ref('')
const studyAge = ref('')
const studyNotes = ref('')
const studyReps = ref(5)
const studyMovements = ref<StudyMovement[]>(STUDY_MOVEMENTS.map(m => m.key))
const fingerOptions = STUDY_MOVEMENTS.filter(m => m.group === 'dedo')
const gestureOptions = STUDY_MOVEMENTS.filter(m => m.group === 'gesto')
const studyBusy = ref(false)
const studyError = ref('')
const studySessions = ref<MirrorStudySession[]>([])

const movementLabel = (key: StudyMovement | null) =>
  STUDY_MOVEMENTS.find(m => m.key === key)?.label ?? ''

// Texto del movimiento detectado, para el panel junto a la vista previa.
const gestureText = computed(() => {
  const g = gesture.value
  if (!g.available) return 'Sin modelo entrenado todavía'
  if (!g.calibrated) return 'Calibra los sensores para ver el movimiento detectado'
  if (!g.label) return 'Sin movimiento reconocido'
  const label = g.label === 'reposo' ? 'Reposo' : movementLabel(g.label as StudyMovement)
  return `${label} (${Math.round(g.confidence * 100)} %)`
})

const canStudy = computed(
  () =>
    !studyBusy.value && !study.value.running && !calibration.value.running && !mirrorActive.value &&
    !demoSensors.value && sensorsReady.value && studyMovements.value.length > 0
)

const studyEstimateMin = computed(() => {
  // 3 s aviso + 10 s reposo inicial + 5 s reposo final + por movimiento: 4 s aviso + reps * 6 s
  const secs = 18 + studyMovements.value.length * (4 + studyReps.value * 6)
  return Math.ceil(secs / 60)
})

const studyProgress = computed(() => {
  const st = study.value
  if (!st.duration) return 0
  return Math.max(0, Math.min(100, (st.elapsed / st.duration) * 100))
})

const studyStepProgress = computed(() => {
  const st = study.value
  if (!st.total_seconds) return 0
  return Math.max(0, Math.min(100, (1 - st.seconds_left / st.total_seconds) * 100))
})

const studyHeadline = computed(() => {
  const st = study.value
  if (st.phase === 'prepare') return st.movement ? `Siguiente: ${movementLabel(st.movement)}` : 'Reposo'
  if (st.phase === 'contract') return `${movementLabel(st.movement)} · repetición ${st.rep} de ${st.reps}`
  if (st.phase === 'relax') return `Relaja · repetición ${st.rep} de ${st.reps}`
  return 'Reposo'
})

const statusText = (s: string | null) =>
  s === 'completa' ? 'Completa' : s === 'cancelada' ? 'Cancelada' : s === 'error' ? 'Con error' : ''

async function loadStudySessions() {
  try {
    studySessions.value = await HandMirrorService.studySessions()
  } catch {
    /* la lista es informativa: se reintenta al terminar el siguiente estudio */
  }
}

function toggleMovement(key: StudyMovement) {
  const i = studyMovements.value.indexOf(key)
  if (i >= 0) studyMovements.value.splice(i, 1)
  else studyMovements.value.push(key)
}

function setGroup(group: 'dedo' | 'gesto', on: boolean) {
  const keys = STUDY_MOVEMENTS.filter(m => m.group === group).map(m => m.key)
  studyMovements.value = studyMovements.value.filter(k => !keys.includes(k))
  if (on) studyMovements.value.push(...keys)
}

async function startStudy() {
  studyBusy.value = true
  studyError.value = ''
  try {
    await HandMirrorService.startStudy({
      name: studyName.value.trim(),
      age: studyAge.value.trim(),
      notes: studyNotes.value.trim(),
      reps: studyReps.value,
      movements: studyMovements.value,
    })
    await refreshMirrorStatus()
  } catch (e: any) {
    studyError.value = e.message || 'No se pudo iniciar el estudio'
  } finally {
    studyBusy.value = false
  }
}

async function cancelStudy() {
  studyBusy.value = true
  try {
    await HandMirrorService.cancelStudy()
    await refreshMirrorStatus()
    await loadStudySessions()
  } catch (e: any) {
    studyError.value = e.message || 'No se pudo cancelar el estudio'
  } finally {
    studyBusy.value = false
  }
}

const calibGesture = ref<CalibrationGesture>('esferico')
const startCalibration = () => runCalibrationAction(() => HandMirrorService.startCalibration(calibGesture.value))
const cancelCalibration = () => runCalibrationAction(() => HandMirrorService.cancelCalibration())
const resetCalibration = () => runCalibrationAction(() => HandMirrorService.resetCalibration())

async function confirmStartMirror() {
  showConfirm.value = false
  busy.value = true
  mirrorError.value = ''
  try {
    const status = await HandMirrorService.start()
    mirrorActive.value = status.active
  } catch (e: any) {
    mirrorError.value = e.message || 'No se pudo iniciar el espejo en tiempo real'
  } finally {
    busy.value = false
  }
}

// Mensaje de la parada de emergencia (core/safety/estop.py): distinto texto
// según lo lance el backend en inglés o español, así que se detecta por
// palabra clave en vez de comparar el string exacto.
const isEstopError = computed(() =>
  /emergency stop|parada de emergencia/i.test(mirrorError.value)
)

async function stopMirror() {
  busy.value = true
  try {
    const status = await HandMirrorService.stop()
    mirrorActive.value = status.active
  } catch (e: any) {
    mirrorError.value = e.message || 'No se pudo detener el espejo en tiempo real'
  } finally {
    busy.value = false
  }
}

onMounted(() => {
  store.startSensorPolling()
  ensureMonitor().then(refreshMirrorStatus)
  loadStudySessions()
  statusPollId = window.setInterval(refreshMirrorStatus, STATUS_POLL_MS)
  monitorPollId = window.setInterval(ensureMonitor, MONITOR_RETRY_MS)
})

onUnmounted(() => {
  store.stopSensorPolling()
  if (statusPollId) clearInterval(statusPollId)
  if (monitorPollId) clearInterval(monitorPollId)
  HandMirrorService.stopMonitor().catch(() => {})
})
</script>

<template>
  <div class="mirror-page">
    <TopHeader title="Espejo en Tiempo Real" crumb="EMGTRAINNER · PACIENTE" />

    <div class="mirror-content">
      <div class="card intro-card">
        <AlertTriangle class="icon-sm" />
        <p>
          Este modo <strong>no sigue el protocolo de gestos</strong> del entrenamiento.
          La mano se mueve de forma continua, en tiempo real, según la fuerza que
          detectan tus sensores en este instante — no clasifica un gesto predefinido.
        </p>
      </div>

      <div class="card sensor-card">
        <div class="sensor-status">
          <span class="status-label">Estado de sensores</span>
          <div class="signal-indicators">
            <div
              v-for="s in emgSignals"
              :key="s.id"
              class="signal-dot"
              :class="s.status === 'active' ? 'dot-on' : 'dot-off'"
            ></div>
          </div>
        </div>
        <div class="sensor-right">
          <span v-if="demoSensors" class="tag-demo">DEMO</span>
          <span class="tag-status" :class="sensorsReady ? 'tag-ok' : 'tag-error'">
            {{ sensorsReady ? 'Sensores listos' : 'Sensores desconectados' }}
          </span>
          <button v-if="!sensorsReady" class="btn-inline" @click="enableDemoSensors">
            <FlaskConical class="icon-sm" /> Modo demo
          </button>
        </div>
      </div>
      <p v-if="demoSensors" class="demo-warning">
        En modo demo los valores son simulados: sirve para probar la pantalla, pero no
        refleja una señal real ni debe usarse para mover la mano física.
      </p>

      <div class="card calib-card">
        <div class="calib-head">
          <div>
            <h3>Calibración</h3>
            <p class="muted">
              Mide tu reposo y una contracción fuerte (~16 s, una sola para todos los sensores) para que la
              mano responda a <em>tu</em> rango y no tiemble en reposo. Repítela cada vez
              que muevas o recoloques los sensores.
            </p>
          </div>
          <span class="tag-status" :class="calibration.calibrated ? 'tag-ok' : 'tag-warn'">
            {{ calibration.calibrated ? 'Calibrado' : 'Sin calibrar' }}
          </span>
        </div>

        <div v-if="calibration.running" class="calib-live">
          <p class="calib-step">Paso {{ calibration.step }} de {{ calibration.steps }}</p>
          <p class="calib-message" :class="{ 'calib-go': calibration.phase === 'measure' }">
            {{ calibration.message }}
          </p>
          <div class="calib-progress">
            <div class="calib-bar">
              <div class="calib-bar-fill" :style="{ width: calibProgress + '%' }"></div>
            </div>
            <span class="calib-count">{{ Math.ceil(calibration.seconds_left) }} s</span>
          </div>
          <button class="btn btn-ghost-outline" :disabled="calibBusy" @click="cancelCalibration">
            Cancelar calibración
          </button>
        </div>

        <template v-else>
          <p v-if="calibration.state === 'error'" class="mirror-error">{{ calibration.error }}</p>
          <p v-else-if="calibration.state === 'done'" class="calib-done">{{ calibration.message }}</p>
          <p v-if="calibError" class="mirror-error">{{ calibError }}</p>
          <p v-if="mirrorActive" class="muted">Detén el espejo para poder calibrar.</p>
          <p v-else-if="study.running" class="muted">Espera a que termine el estudio para poder calibrar.</p>
          <p v-else-if="demoSensors" class="muted">
            No se puede calibrar con el modo demo: los valores son simulados.
            <button v-if="!demoForcedByEnv" class="btn-inline" @click="disableDemoSensors">
              Salir del modo demo
            </button>
            <span v-else>
              (El modo demo está forzado por <code>VITE_SIMULATE_SENSORS=true</code> en
              <code>frontend/.env.local</code>; quítalo y reinicia el frontend.)
            </span>
          </p>
          <div class="calib-actions">
            <label class="study-field study-field-sm">
              <span>Gesto de la contracción</span>
              <select v-model="calibGesture" :disabled="!canCalibrate">
                <option value="esferico">Agarre esférico (pelota)</option>
                <option value="cerrar">Puño cerrado</option>
              </select>
            </label>
            <button class="btn btn-primary" :disabled="!canCalibrate" @click="startCalibration">
              <SlidersHorizontal class="icon-sm" />
              {{ calibration.calibrated ? 'Recalibrar' : 'Calibrar' }}
            </button>
            <button
              v-if="calibration.calibrated"
              class="btn btn-ghost-outline"
              :disabled="calibBusy || mirrorActive"
              @click="resetCalibration"
            >
              <RotateCcw class="icon-sm" /> Borrar calibración
            </button>
          </div>
          <p class="muted calib-hint">
            Aprieta con tu fuerza máxima cómoda. El agarre esférico (como sujetar una pelota) es el
            que más se distingue del reposo con estos sensores; si un puño flojo no pasa, prueba con
            él. Un sensor que no distingue la contracción del ruido del reposo se ignora.
          </p>
        </template>

        <div v-if="calibration.calibrated" class="channel-bars">
          <div v-for="(cal, i) in calibration.channels" :key="i" class="channel-row">
            <span class="channel-name">Sensor {{ i + 1 }}</span>
            <div class="channel-track">
              <div
                v-if="cal"
                class="channel-fill"
                :style="{ width: Math.round((channelLevels[i] ?? 0) * 100) + '%' }"
              ></div>
            </div>
            <span class="channel-pct">
              {{ cal ? Math.round((channelLevels[i] ?? 0) * 100) + '%' : 'no usado' }}
            </span>
            <span v-if="cal" class="channel-quality" :class="{ 'quality-low': cal.separation < 0.4 }">
              señal {{ Math.round(cal.separation * 100) }} %
            </span>
          </div>
        </div>
      </div>

      <div class="card study-card">
        <div class="calib-head">
          <div>
            <h3>Estudio de calibración</h3>
            <p class="muted">
              Reposo, luego cada dedo por separado y después gestos completos de la mano
              (cerrar, abrir, apuntar, pinza…), con varias repeticiones (~{{ studyEstimateMin }} min).
              Cada sesión se guarda con su señal etiquetada y sus parámetros, para entrenar
              después el modelo que detecta cada dedo y gesto. No mueve la mano.
            </p>
          </div>
          <span v-if="study.running" class="tag-status tag-error">Grabando</span>
        </div>

        <div v-if="study.running" class="calib-live">
          <p class="calib-step">Paso {{ study.step }} de {{ study.steps }}</p>
          <p class="study-headline">{{ studyHeadline }}</p>
          <p class="calib-message" :class="{ 'calib-go': study.phase === 'contract' }">{{ study.message }}</p>
          <div class="calib-progress">
            <div class="calib-bar">
              <div class="calib-bar-fill" :style="{ width: studyStepProgress + '%' }"></div>
            </div>
            <span class="calib-count">{{ Math.ceil(study.seconds_left) }} s</span>
          </div>
          <div class="calib-progress">
            <div class="calib-bar calib-bar-thin">
              <div class="calib-bar-fill study-total" :style="{ width: studyProgress + '%' }"></div>
            </div>
            <span class="calib-count">{{ Math.round(studyProgress) }} %</span>
          </div>
          <p class="muted">{{ study.rows }} lecturas guardadas · carpeta {{ study.file }}</p>
          <button class="btn btn-ghost-outline" :disabled="studyBusy" @click="cancelStudy">
            Cancelar (se conserva lo grabado)
          </button>
        </div>

        <template v-else>
          <div class="study-form">
            <label class="study-field">
              <span>Participante</span>
              <input v-model="studyName" type="text" maxlength="40" placeholder="Nombre (por defecto Guest)" />
            </label>
            <label class="study-field study-field-sm">
              <span>Edad</span>
              <input v-model="studyAge" type="text" maxlength="3" placeholder="—" />
            </label>
            <label class="study-field study-field-sm">
              <span>Repeticiones</span>
              <select v-model.number="studyReps">
                <option :value="3">3 por dedo</option>
                <option :value="5">5 por dedo</option>
                <option :value="8">8 por dedo</option>
              </select>
            </label>
          </div>
          <div class="study-fingers">
            <span class="study-label">Dedos</span>
            <label v-for="m in fingerOptions" :key="m.key" class="study-check">
              <input type="checkbox" :checked="studyMovements.includes(m.key)" @change="toggleMovement(m.key)" />
              {{ m.label }}
            </label>
            <button class="btn-link" type="button" @click="setGroup('dedo', !fingerOptions.every(m => studyMovements.includes(m.key)))">
              {{ fingerOptions.every(m => studyMovements.includes(m.key)) ? 'Quitar todos' : 'Todos' }}
            </button>
          </div>
          <div class="study-fingers">
            <span class="study-label">Gestos</span>
            <label v-for="m in gestureOptions" :key="m.key" class="study-check">
              <input type="checkbox" :checked="studyMovements.includes(m.key)" @change="toggleMovement(m.key)" />
              {{ m.label }}
            </label>
            <button class="btn-link" type="button" @click="setGroup('gesto', !gestureOptions.every(m => studyMovements.includes(m.key)))">
              {{ gestureOptions.every(m => studyMovements.includes(m.key)) ? 'Quitar todos' : 'Todos' }}
            </button>
          </div>
          <label class="study-field">
            <span>Notas (colocación de la correa, postura, observaciones)</span>
            <input
              v-model="studyNotes"
              type="text"
              maxlength="500"
              placeholder="Ej.: correa en flexores, tercio proximal, antebrazo apoyado"
            />
          </label>

          <p v-if="study.state === 'done'" class="calib-done">{{ study.message }} Carpeta: {{ study.file }}</p>
          <p v-else-if="study.state === 'error'" class="mirror-error">{{ study.error }}</p>
          <p v-else-if="study.message" class="muted">{{ study.message }}</p>
          <p v-if="studyError" class="mirror-error">{{ studyError }}</p>
          <p v-if="mirrorActive" class="muted">Detén el espejo para iniciar el estudio.</p>
          <p v-else-if="calibration.running" class="muted">Espera a que termine la calibración.</p>
          <p v-else-if="demoSensors" class="muted">No se puede grabar con el modo demo: los valores son simulados.</p>

          <div class="calib-actions">
            <button class="btn btn-primary" :disabled="!canStudy" @click="startStudy">
              <ClipboardList class="icon-sm" /> Iniciar estudio
            </button>
          </div>
          <p class="muted calib-hint">
            En los dedos, mueve solo el indicado y mantén el resto relajado; en los gestos, hazlos completos y con fuerza cómoda. Usa la misma postura y
            colocación de la correa en todas las sesiones; cámbialas solo si lo anotas.
          </p>
        </template>

        <div v-if="studySessions.length" class="study-list">
          <span class="study-label">Sesiones guardadas ({{ studySessions.length }})</span>
          <div v-for="s in studySessions.slice(0, 8)" :key="s.id" class="study-row">
            <span class="study-row-name">{{ s.participant }}</span>
            <span class="study-row-meta">
              {{ s.created_at ? s.created_at.replace('T', ' ') : s.id }} ·
              {{ s.movements.length }} movimientos × {{ s.reps ?? '?' }} · {{ s.rows }} lecturas
            </span>
            <span class="tag-status" :class="s.status === 'completa' ? 'tag-ok' : 'tag-warn'">{{ statusText(s.status) }}</span>
          </div>
        </div>
      </div>

      <div class="mirror-grid">
        <div class="card chart-card">
          <h3>Señal en vivo</h3>
          <div class="chart-wrapper">
            <EmgSerialPlotter
              :websocket-url="() => buildAuthenticatedWebSocketUrl('/v1/monitoring/sensor/ws/emg-stream')"
              :is-running="true"
            />
          </div>
        </div>

        <div class="card hand-card">
          <h3>Vista previa</h3>
          <MirrorHandVisualization :activation="activation" :connected="previewConnected" />
          <div class="gesture-panel" :class="{ 'gesture-panel-active': gesture.label }">
            <span class="gesture-caption">Movimiento detectado</span>
            <span class="gesture-value">{{ gestureText }}</span>
          </div>
        </div>
      </div>

      <div class="card control-card">
        <div class="control-info">
          <h3>Mano robótica</h3>
          <p class="muted">
            {{
              mirrorActive
                ? 'La mano está siguiendo la señal en tiempo real.'
                : 'La mano física está detenida; solo se ve la vista previa en pantalla.'
            }}
          </p>
          <p v-if="mirrorError" class="mirror-error">{{ mirrorError }}</p>
          <p v-if="isEstopError" class="mirror-hint">
            La parada de emergencia está activada (se reactiva sola en cada reinicio del backend).
            Abre el ícono de engranaje ⚙️ en la parte superior y en
            <strong>«Seguridad de movimiento»</strong> pulsa <strong>Resetear</strong>, luego
            vuelve a intentar «Iniciar espejo».
          </p>
        </div>
        <button
          v-if="!mirrorActive"
          class="btn btn-primary"
          :disabled="busy || !sensorsReady || calibration.running || !calibration.calibrated"
          :title="!sensorsReady ? 'Se requieren sensores activos para mover la mano' : !calibration.calibrated ? 'Calibra los sensores primero' : ''"
          @click="showConfirm = true"
        >
          <Play class="icon-sm" /> Iniciar espejo
        </button>
        <button v-else class="btn btn-stop" :disabled="busy" @click="stopMirror">
          <Square class="icon-sm" /> Detener
        </button>
      </div>
    </div>

    <!-- Confirmación antes de mover la mano física -->
    <div v-if="showConfirm" class="modal-backdrop">
      <div class="modal" role="dialog" aria-modal="true">
        <h2 class="modal-title">¿Mover la mano ahora?</h2>
        <p class="modal-subtitle">
          La mano robótica empezará a moverse sola, siguiendo la fuerza de la señal
          sEMG en tiempo real. Asegúrate de que esté libre de obstáculos.
        </p>
        <div class="modal-actions">
          <button class="btn btn-ghost-outline" @click="showConfirm = false">Cancelar</button>
          <button class="btn btn-primary" @click="confirmStartMirror">Sí, iniciar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mirror-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.mirror-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
}

.intro-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px 16px;
  color: #92400e;
  background: #fffbeb;
  border-color: #fde68a;
  font-size: 13.5px;
  line-height: 1.5;
}
.intro-card :deep(svg) { flex-shrink: 0; margin-top: 2px; }

.sensor-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  flex-wrap: wrap;
  gap: 10px;
}
.sensor-status { display: flex; align-items: center; gap: 12px; }
.status-label { font-size: 13px; font-weight: 600; color: #334155; }
.signal-indicators { display: flex; gap: 6px; }
.signal-dot { width: 12px; height: 12px; border-radius: 50%; }
.dot-on { background: #22c55e; }
.dot-off { background: #ef4444; }

.sensor-right { display: flex; align-items: center; gap: 8px; }
.tag-demo {
  font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;
  background: #f59e0b; color: white;
}
.tag-status { font-size: 12.5px; font-weight: 600; padding: 4px 10px; border-radius: 999px; }
.tag-ok { background: #dcfce7; color: #15803d; }
.tag-error { background: #fee2e2; color: #b91c1c; }
.tag-warn { background: #fef3c7; color: #92400e; }

.calib-card { padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.calib-card h3 { margin: 0 0 4px; font-size: 14px; font-weight: 600; }
.calib-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.calib-live { display: flex; flex-direction: column; gap: 8px; align-items: flex-start; }
.calib-step { margin: 0; font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }
.calib-message { margin: 0; font-size: 16px; font-weight: 600; color: #334155; }
.calib-message.calib-go { color: #b91c1c; }
.calib-progress { display: flex; align-items: center; gap: 10px; width: 100%; max-width: 480px; }
.calib-bar { flex: 1; height: 10px; background: #e2e8f0; border-radius: 999px; overflow: hidden; }
.calib-bar-fill { height: 100%; background: #2563eb; transition: width 0.2s linear; }
.calib-count { font-size: 13px; font-weight: 600; color: #334155; min-width: 34px; text-align: right; }
.calib-done { margin: 0; font-size: 13px; color: #15803d; font-weight: 600; }
.calib-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.calib-hint { font-size: 12px; margin: 0; }

.channel-bars { display: flex; flex-direction: column; gap: 6px; padding-top: 4px; }
.channel-row { display: flex; align-items: center; gap: 10px; font-size: 12.5px; }
.channel-name { width: 64px; color: #334155; font-weight: 600; }
.channel-track { flex: 1; height: 8px; background: #e2e8f0; border-radius: 999px; overflow: hidden; }
.channel-fill { height: 100%; background: #16a34a; transition: width 0.15s linear; }
.channel-quality { width: 84px; font-size: 11.5px; color: #15803d; }
.channel-quality.quality-low { color: #b45309; }
.channel-pct { width: 64px; text-align: right; color: #64748b; }

.btn-inline {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 10px; font-size: 12.5px; font-weight: 600;
  border: 1px solid #fde68a; background: #fffbeb; color: #92400e;
  border-radius: 6px; cursor: pointer;
}

.study-card { padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.study-card h3 { margin: 0 0 4px; font-size: 14px; font-weight: 600; }
.study-headline { margin: 0; font-size: 22px; font-weight: 700; color: #0f172a; }
.calib-bar-thin { height: 6px; }
.study-total { background: #64748b; }
.study-form { display: flex; gap: 10px; flex-wrap: wrap; }
.study-field { display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: #475569; flex: 1; min-width: 200px; }
.study-field-sm { flex: 0 0 auto; min-width: 110px; }
.study-field input, .study-field select {
  padding: 8px 10px; font-size: 13px; font-weight: 400; color: #0f172a;
  border: 1px solid #e2e8f0; border-radius: 6px; background: white;
}
.study-fingers { display: flex; gap: 14px; flex-wrap: wrap; align-items: center; }
.btn-link { background: none; border: none; padding: 0; font-size: 12.5px; font-weight: 600; color: #2563eb; cursor: pointer; }
.study-label { font-size: 12px; font-weight: 600; color: #475569; min-width: 46px; }
.study-check { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: #334155; cursor: pointer; }
.study-list { display: flex; flex-direction: column; gap: 6px; padding-top: 6px; border-top: 1px solid #e2e8f0; }
.study-row { display: flex; align-items: center; gap: 10px; font-size: 12.5px; flex-wrap: wrap; }
.study-row-name { font-weight: 600; color: #334155; min-width: 90px; }
.study-row-meta { color: #64748b; flex: 1; }

.demo-warning { font-size: 12.5px; color: #92400e; margin: -6px 2px 0; }

.mirror-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 14px;
}
@media (max-width: 800px) {
  .mirror-grid { grid-template-columns: 1fr; }
}

.chart-card, .hand-card, .control-card { padding: 16px; }
.chart-card h3, .hand-card h3, .control-card h3 { margin: 0 0 10px; font-size: 14px; font-weight: 600; }
.chart-wrapper { height: 260px; }

.gesture-panel {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}
.gesture-panel-active { background: #eff6ff; border-color: #bfdbfe; }
.gesture-caption { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }
.gesture-value { font-size: 14px; font-weight: 600; color: #0f172a; }
.gesture-panel-active .gesture-value { color: #1d4ed8; }

.control-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.control-info h3 { margin-bottom: 4px; }
.mirror-error { color: #b91c1c; font-size: 12.5px; margin-top: 4px; }
.mirror-hint {
  color: #92400e;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 12.5px;
  line-height: 1.5;
  margin-top: 6px;
  max-width: 420px;
}

.btn-stop {
  background: white; color: #b91c1c; border: 1px solid #fecaca;
}
.btn-stop:hover { background: #fef2f2; }

.btn-ghost-outline {
  background: white; border: 1px solid #e2e8f0; color: #334155;
}

.modal-backdrop {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.5);
  display: flex; align-items: center; justify-content: center; z-index: 50;
  padding: 16px;
}
.modal {
  background: white; border-radius: 12px; padding: 24px;
  max-width: 420px; width: 100%; box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}
.modal-title { margin: 0 0 8px; font-size: 18px; }
.modal-subtitle { margin: 0 0 20px; font-size: 13.5px; color: #475569; line-height: 1.5; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
</style>
