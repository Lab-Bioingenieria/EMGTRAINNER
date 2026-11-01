import { authService } from './auth.service'

/**
 * Interlock de emergencia (`core/safety/estop.py`) que protege cualquier
 * comando de movimiento de la mano. Es fail-closed: arranca ENGAGED cada
 * vez que se reinicia el backend, así que hay que resetearlo a mano antes
 * de poder mover motores (entrenamiento, Espejo en Tiempo Real, etc.).
 *
 * Montado en la raíz (`/hand/safety/...`, no bajo `/v1`), igual que
 * `/hand/*` — por eso usa `authService.authFetch` en vez de la instancia
 * de axios de `lib/api.ts`.
 */
export interface SafetyState {
    engaged: boolean
    reason: string | null
    actor: string | null
    changed_at: string
}

async function parseOrThrow(res: Response): Promise<SafetyState> {
    if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || err.message || 'No se pudo completar la operación')
    }
    return res.json()
}

export class SafetyService {
    static async status(): Promise<SafetyState> {
        const res = await authService.authFetch('/hand/safety/status')
        return parseOrThrow(res)
    }

    static async reset(): Promise<SafetyState> {
        const res = await authService.authFetch('/hand/safety/reset', { method: 'POST' })
        return parseOrThrow(res)
    }

    static async engage(reason?: string): Promise<SafetyState> {
        const res = await authService.authFetch('/hand/safety/estop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: reason || null }),
        })
        return parseOrThrow(res)
    }
}
