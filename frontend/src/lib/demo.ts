import { ref } from "vue";

/**
 * Modo demo de sensores.
 *
 * El estado de las señales sEMG se lee del dispositivo real. Cuando no hay
 * hardware conectado (desarrollo, pruebas de flujo, sustentación sin el ESP32)
 * este interruptor simula los 3 canales como activos para poder recorrer todo
 * el flujo doctor/paciente.
 *
 * Se activa de dos formas:
 *   1. Variable de entorno, en `frontend/.env.local`:
 *        VITE_SIMULATE_SENSORS=true
 *   2. Desde la interfaz, con el botón "Usar modo demo" que aparece cuando no
 *      se detectan sensores (queda guardado en localStorage por navegador).
 *
 * Mientras está activo, la interfaz muestra un distintivo MODO DEMO para que
 * nunca se confunda una sesión simulada con una medición real.
 */

const STORAGE_KEY = "emgt_demo_sensors";

function readInitial(): boolean {
    if (import.meta.env?.VITE_SIMULATE_SENSORS === "true") return true;
    try {
        return localStorage.getItem(STORAGE_KEY) === "1";
    } catch {
        return false;
    }
}

/** Reactivo: cualquier vista que lo use se actualiza sola. */
export const demoSensors = ref<boolean>(readInitial());

/** Forzado por variable de entorno: no se puede apagar desde la interfaz. */
export const demoForcedByEnv: boolean = import.meta.env?.VITE_SIMULATE_SENSORS === "true";

export function setDemoSensors(enabled: boolean): void {
    if (demoForcedByEnv) return;
    demoSensors.value = enabled;
    try {
        if (enabled) localStorage.setItem(STORAGE_KEY, "1");
        else localStorage.removeItem(STORAGE_KEY);
    } catch {
        /* almacenamiento no disponible: el modo dura lo que la pestaña */
    }
}

export function toggleDemoSensors(): void {
    setDemoSensors(!demoSensors.value);
}
