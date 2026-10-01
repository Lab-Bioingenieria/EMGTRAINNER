import { authService } from './auth.service'

/**
 * Modo "Espejo en Tiempo Real": mueve la mano de forma continua segun la
 * amplitud cruda de los sensores, sin seguir el protocolo de gestos.
 *
 * El backend monta este router en la raiz (`/hand/mirror/...`, no bajo
 * `/v1`), igual que `/hand/*` — por eso usa `authService.authFetch` en vez
 * de la instancia de axios de `lib/api.ts`, que antepone `/v1`.
 */
export interface MirrorChannelCalibration {
    rest: number
    rest_sigma: number
    floor: number
    ceil: number
    /** Fraccion (0..1) de la contraccion que supera el ruido del reposo: calidad del canal. */
    separation: number
}

export type CalibrationGesture = 'esferico' | 'cerrar'

export interface MirrorCalibrationStatus {
    /** idle | running | done | error */
    state: 'idle' | 'running' | 'done' | 'error'
    /** prepare (aviso) | measure (midiendo) | null */
    phase: 'prepare' | 'measure' | null
    /** 1 = reposo, 2.. = contraccion de cada sensor */
    step: number
    steps: number
    /** sensor (0-based) que se contrae en este paso, o null en el reposo */
    channel: number | null
    /** Gesto de la contraccion de esta calibracion. */
    gesture: CalibrationGesture | null
    seconds_left: number
    total_seconds: number
    message: string
    error: string | null
    running: boolean
    calibrated: boolean
    channels: (MirrorChannelCalibration | null)[]
}

export type StudyMovement =
    | 'pulgar' | 'indice' | 'medio' | 'anular' | 'menique'
    | 'cerrar' | 'abrir' | 'apuntar' | 'pinza' | 'like' | 'cilindrico' | 'esferico'

/** Movimientos del estudio, en el orden del protocolo: primero los dedos, luego los gestos. */
export const STUDY_MOVEMENTS: { key: StudyMovement; label: string; group: 'dedo' | 'gesto' }[] = [
    { key: 'pulgar', label: 'Pulgar', group: 'dedo' },
    { key: 'indice', label: 'Índice', group: 'dedo' },
    { key: 'medio', label: 'Medio', group: 'dedo' },
    { key: 'anular', label: 'Anular', group: 'dedo' },
    { key: 'menique', label: 'Meñique', group: 'dedo' },
    { key: 'cerrar', label: 'Cerrar', group: 'gesto' },
    { key: 'abrir', label: 'Abrir', group: 'gesto' },
    { key: 'apuntar', label: 'Apuntar', group: 'gesto' },
    { key: 'pinza', label: 'Pinza', group: 'gesto' },
    { key: 'like', label: 'Like', group: 'gesto' },
    { key: 'cilindrico', label: 'Cilíndrico', group: 'gesto' },
    { key: 'esferico', label: 'Esférico', group: 'gesto' },
]

export interface MirrorStudyStatus {
    /** idle | running | done | error */
    state: 'idle' | 'running' | 'done' | 'error'
    /** prepare (aviso) | rest | contract | relax | null */
    phase: 'prepare' | 'rest' | 'contract' | 'relax' | null
    step: number
    steps: number
    /** Movimiento (dedo o gesto) del bloque actual, o null en el reposo. */
    movement: StudyMovement | null
    rep: number
    reps: number
    seconds_left: number
    /** Duracion del paso actual. */
    total_seconds: number
    /** Segundos transcurridos / duracion prevista del estudio completo. */
    elapsed: number
    duration: number
    message: string
    error: string | null
    /** Carpeta de la sesion guardada (relativa a `storage/calibration_studies`), o null. */
    file: string | null
    rows: number
    running: boolean
}

export interface MirrorStudySession {
    id: string
    participant: string
    created_at: string | null
    status: 'completa' | 'cancelada' | 'error' | null
    rows: number
    seconds: number
    movements: StudyMovement[]
    reps: number | null
}

export interface MirrorStudyStart {
    name?: string
    age?: string
    notes?: string
    reps?: number
    movements?: StudyMovement[]
}

/** Movimientos que puede reconocer el clasificador entrenado (ver
 * `backend/scripts/train_gesture_classifier.py`): los 7 gestos + los 5 dedos del Estudio de
 * calibración, más "reposo". El modelo entrena con las sesiones del protocolo (solo gestos)
 * Y las del Estudio (gestos + dedos sueltos): cuántas clases reconoce bien depende de cuántas
 * sesiones haya de cada una — con pocas sesiones de estudio, los dedos sueltos casi no se
 * reconocen todavía (ver `claude/clasificador-de-movimientos.md`). */
export type GestureLabel = StudyMovement | 'reposo'

export interface MirrorGestureStatus {
    /** Hay un modelo entrenado cargado (`backend/storage/models/gesture_classifier.json`). */
    available: boolean
    /** Hay una calibración vigente: el clasificador necesita el reposo de referencia para funcionar. */
    calibrated: boolean
    /** Movimiento detectado ahora mismo, o null si falta el modelo/calibración o la confianza es baja. */
    label: GestureLabel | null
    /** Confianza (0..1) del movimiento detectado; 0 si `label` es null. */
    confidence: number
}

export interface MirrorStatus {
    /** El lazo que mueve la mano fisica esta corriendo. */
    active: boolean
    /** Ultimo cierre aplicado a la mano fisica (0..1). */
    activation: number
    last_error: string | null
    /** El monitor de la pantalla mantiene el streaming encendido (sin grabar). */
    monitoring: boolean
    /** Llegan muestras recientes de los sensores. */
    signal: boolean
    /** Cierre 0..1 que piden los sensores ahora mismo (vista previa). */
    live: number
    /** Nivel calibrado 0..1 de cada canal (vacio si aun no hay calibracion). */
    channels: number[]
    calibration: MirrorCalibrationStatus
    study: MirrorStudyStatus
    /** Movimiento detectado por el clasificador entrenado (solo informativo: no mueve la mano). */
    gesture: MirrorGestureStatus
}

async function parseOrThrow(res: Response): Promise<MirrorStatus> {
    if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || err.message || 'No se pudo completar la operación')
    }
    return res.json()
}

export class HandMirrorService {
    static async start(): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/start', { method: 'POST' })
        return parseOrThrow(res)
    }

    static async stop(): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/stop', { method: 'POST' })
        return parseOrThrow(res)
    }

    static async status(): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/status')
        return parseOrThrow(res)
    }

    /** Enciende el streaming (sin grabar) mientras la pantalla esta abierta; se renueva con cada `status()`. */
    static async startMonitor(): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/monitor/start', { method: 'POST' })
        return parseOrThrow(res)
    }

    static async stopMonitor(): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/monitor/stop', { method: 'POST' })
        return parseOrThrow(res)
    }

    /** Inicia el estudio de calibracion (guarda la sesion en el backend). */
    static async startStudy(options: MirrorStudyStart = {}): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/study/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: options.name || null,
                age: options.age || null,
                notes: options.notes || null,
                reps: options.reps ?? 5,
                movements: options.movements?.length ? options.movements : null,
            }),
        })
        return parseOrThrow(res)
    }

    static async cancelStudy(): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/study/cancel', { method: 'POST' })
        return parseOrThrow(res)
    }

    /** Sesiones del estudio ya guardadas, las mas recientes primero. */
    static async studySessions(): Promise<MirrorStudySession[]> {
        const res = await authService.authFetch('/hand/mirror/study/sessions')
        if (!res.ok) throw new Error('No se pudo leer la lista de sesiones')
        return (await res.json()).sessions
    }

    static async startCalibration(gesture: CalibrationGesture = 'esferico'): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/calibration/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gesture }),
        })
        return parseOrThrow(res)
    }

    static async cancelCalibration(): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/calibration/cancel', { method: 'POST' })
        return parseOrThrow(res)
    }

    static async resetCalibration(): Promise<MirrorStatus> {
        const res = await authService.authFetch('/hand/mirror/calibration/reset', { method: 'POST' })
        return parseOrThrow(res)
    }
}
