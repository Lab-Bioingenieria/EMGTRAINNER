import { defineStore } from "pinia";
import type { Gesture, TrainingMode, EmgSignal } from "../lib/constants";
import { DEFAULT_DEVICE_ID } from "../lib/constants";
import { EmgService } from "../services/emg.service";
import { demoSensors } from "../lib/demo";

/**
 * Estado compartido de la sesion supervisada (doctor <-> paciente).
 *
 * El estado autoritativo vive en el backend (`/ws/live-session`). Este store
 * es un espejo local: envia acciones y aplica el snapshot que devuelve el
 * servidor. Por eso el codigo de sesion se genera UNA sola vez, en el servidor,
 * y es identico en todas las pantallas de ambos lados.
 */

export type SessionPhase =
    | "setup"
    | "waiting"
    | "connected"
    | "ready"
    | "running"
    | "paused"
    | "finished";

export type SessionRole = "doctor" | "patient";

export type LinkStatus = "idle" | "connecting" | "open" | "closed" | "error";

export interface LiveStateSnapshot {
    code: string;
    protocolName: string;
    trainingMode: TrainingMode | null;
    gestures: Gesture[];
    gestureDuration: number;
    restTime: number;
    repetitions: number;
    phase: Exclude<SessionPhase, "setup">;
    currentStep: number;
    currentGesture: string;
    totalSteps: number;
    completedSteps: number;
    csvFilename: string;
    durationSeconds: number;
    finishedAt: string;
    patientName: string;
    patientConnected: boolean;
    patientReady: boolean;
    doctorConnected: boolean;
}

const LIVE_SESSION_PATH = "/ws/live-session";

function buildSocketUrl(role: SessionRole, code?: string): string {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const params = new URLSearchParams({ role });
    if (code) params.set("code", code);
    return `${protocol}//${window.location.host}${LIVE_SESSION_PATH}?${params.toString()}`;
}

export interface SessionState {
    role: SessionRole | null;
    sessionCode: string;
    linkStatus: LinkStatus;
    linkError: string;

    protocolName: string;
    trainingMode: TrainingMode | null;
    selectedGestures: Gesture[];
    gestureDuration: number;
    restTime: number;
    repetitions: number;

    phase: SessionPhase;
    currentStep: number;
    currentGesture: string;
    totalSteps: number;
    completedSteps: number;
    csvFilename: string;
    durationSeconds: number;
    finishedAt: string;
    patientName: string;
    patientConnected: boolean;
    patientReady: boolean;
    doctorConnected: boolean;

    emgSignals: EmgSignal[];
    sensorsOnline: boolean;

    sessionTime: number;
}

export const useSessionStore = defineStore("session", {
    state: (): SessionState => ({
        // --- Identidad del canal ---
        role: null as SessionRole | null,
        sessionCode: "",
        linkStatus: "idle" as LinkStatus,
        linkError: "" as string,

        // --- Configuracion del protocolo (la define el doctor) ---
        protocolName: "",
        trainingMode: null as TrainingMode | null,
        selectedGestures: [] as Gesture[],
        gestureDuration: 5,
        restTime: 5,
        repetitions: 3,

        // --- Estado del flujo ---
        phase: "setup" as SessionPhase,
        currentStep: 0,
        currentGesture: "",
        totalSteps: 0,
        completedSteps: 0,
        csvFilename: "",
        durationSeconds: 0,
        finishedAt: "",
        patientName: "",
        patientConnected: false,
        patientReady: false,
        doctorConnected: false,

        // --- Sensores sEMG (estado real del dispositivo) ---
        emgSignals: [
            { id: 1, name: "Canal 1", status: "inactive" },
            { id: 2, name: "Canal 2", status: "inactive" },
            { id: 3, name: "Canal 3", status: "inactive" },
        ] as EmgSignal[],
        sensorsOnline: false,

        sessionTime: 0,
    }),

    getters: {
        activeSignals: (state: SessionState): number =>
            state.emgSignals.filter((s) => s.status === "active").length,
        /** El doctor no puede publicar el codigo sin las 3 senales activas. */
        sensorsReady: (state: SessionState): boolean =>
            state.emgSignals.filter((s) => s.status === "active").length >= 3,
        /** El boton "Iniciar" del doctor solo se habilita si el paciente confirmo. */
        canStartSession: (state: SessionState): boolean =>
            state.patientReady &&
            state.emgSignals.filter((s) => s.status === "active").length >= 3,
        isLinked: (state: SessionState): boolean => state.linkStatus === "open",
    },

    actions: {
        // ------------------------------------------------------------ socket

        _openSocket(role: SessionRole, code?: string): Promise<void> {
            this.closeLink();
            this.role = role;
            this.linkStatus = "connecting";
            this.linkError = "";

            return new Promise((resolve, reject) => {
                let socket: WebSocket;
                try {
                    socket = new WebSocket(buildSocketUrl(role, code));
                } catch (error) {
                    this.linkStatus = "error";
                    this.linkError = "No se pudo abrir el canal de sesion.";
                    reject(error);
                    return;
                }

                let settled = false;

                socket.onmessage = (event) => {
                    let message: any;
                    try {
                        message = JSON.parse(event.data);
                    } catch {
                        return;
                    }

                    if (message.type === "state") {
                        this.applySnapshot(message.state as LiveStateSnapshot);
                        if (!settled) {
                            settled = true;
                            this.linkStatus = "open";
                            resolve();
                        }
                    } else if (message.type === "error") {
                        this.linkError = message.message || "Codigo de sesion invalido.";
                        this.linkStatus = "error";
                        if (!settled) {
                            settled = true;
                            reject(new Error(message.reason || "invalid_code"));
                        }
                    }
                };

                socket.onerror = () => {
                    this.linkStatus = "error";
                    if (!this.linkError) {
                        this.linkError = "No hay conexion con el servidor de sesiones.";
                    }
                    if (!settled) {
                        settled = true;
                        reject(new Error("socket_error"));
                    }
                };

                socket.onclose = () => {
                    if (this.linkStatus !== "error") this.linkStatus = "closed";
                    if (!settled) {
                        settled = true;
                        reject(new Error("socket_closed"));
                    }
                };

                liveSocket = socket;
            });
        },

        _send(payload: Record<string, unknown>) {
            if (liveSocket && liveSocket.readyState === WebSocket.OPEN) {
                liveSocket.send(JSON.stringify(payload));
            }
        },

        closeLink() {
            if (liveSocket) {
                liveSocket.onclose = null;
                liveSocket.onerror = null;
                liveSocket.onmessage = null;
                try {
                    liveSocket.close();
                } catch {
                    /* ignorado */
                }
                liveSocket = null;
            }
            if (this.linkStatus !== "error") this.linkStatus = "idle";
        },

        applySnapshot(snapshot: LiveStateSnapshot) {
            this.sessionCode = snapshot.code;
            this.protocolName = snapshot.protocolName;
            this.trainingMode = snapshot.trainingMode;
            this.selectedGestures = snapshot.gestures || [];
            this.gestureDuration = snapshot.gestureDuration;
            this.restTime = snapshot.restTime;
            this.repetitions = snapshot.repetitions;
            this.currentStep = snapshot.currentStep;
            this.currentGesture = snapshot.currentGesture;
            this.totalSteps = snapshot.totalSteps;
            this.completedSteps = snapshot.completedSteps;
            this.csvFilename = snapshot.csvFilename;
            this.durationSeconds = snapshot.durationSeconds;
            this.finishedAt = snapshot.finishedAt;
            this.patientName = snapshot.patientName;
            this.patientConnected = snapshot.patientConnected;
            this.patientReady = snapshot.patientReady;
            this.doctorConnected = snapshot.doctorConnected;
            this.phase = snapshot.phase;
        },

        // ------------------------------------------------- ciclo de vida doctor

        /**
         * Abre la sala del doctor. El servidor devuelve el codigo definitivo,
         * que ya no vuelve a cambiar durante toda la sesion.
         */
        async openDoctorSession() {
            await this._openSocket("doctor");
        },

        setTrainingMode(mode: TrainingMode | null) {
            this.trainingMode = mode;
            if (mode === null) {
                this.selectedGestures = [];
            }
            this.pushConfig();
        },

        setSelectedGestures(gestures: Gesture[]) {
            this.selectedGestures = gestures;
            this.pushConfig();
        },

        setProtocolParams(params: { protocolName?: string; repetitions?: number; restTime?: number; gestureDuration?: number }) {
            if (params.protocolName !== undefined) this.protocolName = params.protocolName;
            if (params.repetitions !== undefined) this.repetitions = params.repetitions;
            if (params.restTime !== undefined) this.restTime = params.restTime;
            if (params.gestureDuration !== undefined) this.gestureDuration = params.gestureDuration;
            this.pushConfig();
        },

        pushConfig() {
            this._send({
                type: "config",
                protocolName: this.protocolName,
                trainingMode: this.trainingMode,
                gestures: JSON.parse(JSON.stringify(this.selectedGestures)),
                gestureDuration: this.gestureDuration,
                restTime: this.restTime,
                repetitions: this.repetitions,
            });
        },

        /** Publica el codigo y pasa a la pantalla de espera. */
        startWaiting() {
            this.pushConfig();
            this.phase = "waiting";
            this._send({ type: "start_waiting" });
        },

        /** Boton "Iniciar" del doctor: habilita la pantalla de gestos del paciente. */
        startSession() {
            if (!this.canStartSession) return;
            this._send({ type: "start" });
        },

        pauseSession() {
            this._send({ type: "pause" });
        },

        resumeSession() {
            this._send({ type: "resume" });
        },

        finishSession(durationSeconds?: number) {
            this._send({
                type: "finish",
                durationSeconds: durationSeconds ?? this.sessionTime,
            });
        },

        // ----------------------------------------------- ciclo de vida paciente

        /**
         * Valida el codigo contra el servidor. Si no corresponde a ninguna
         * sesion activa, la promesa se rechaza y el paciente NO avanza.
         */
        async connectAsPatient(code: string, patientName = "") {
            await this._openSocket("patient", code.trim());
            if (patientName) {
                this._send({ type: "identify", patientName });
            }
        },

        /** El paciente confirmo los protocolos de inicio y queda a la espera. */
        markPatientReady() {
            this._send({ type: "ready" });
        },

        /** Avance del paciente: indice, gesto en curso y totales del circuito. */
        reportStep(step: number, gestureName = "", totalSteps = 0, completedSteps = 0) {
            this.currentStep = step;
            this.currentGesture = gestureName;
            this.totalSteps = totalSteps;
            this.completedSteps = completedSteps;
            this._send({ type: "step", step, gestureName, totalSteps, completedSteps });
        },

        /** Adjunta el CSV generado a la sesion, sin cambiar de fase. */
        reportResult(csvFilename: string, durationSeconds: number, completedSteps: number) {
            this._send({ type: "result", csvFilename, durationSeconds, completedSteps });
        },

        // --------------------------------------------------------- utilidades

        incrementTime() {
            this.sessionTime++;
        },

        resetSession() {
            this.phase = "setup";
            this.sessionTime = 0;
            this.trainingMode = null;
            this.selectedGestures = [];
            this.currentStep = 0;
            this.patientReady = false;
            this.protocolName = "";
            this._send({ type: "reset" });
        },

        /** Lee el estado real del dispositivo sEMG y lo refleja en los 3 canales. */
        async refreshSensors() {
            // Modo demo: se simulan los 3 canales activos, sin consultar hardware.
            if (demoSensors.value) {
                const on: EmgSignal["status"] = "active";
                this.sensorsOnline = true;
                this.emgSignals = this.emgSignals.map((s) => ({ ...s, status: on }));
                return;
            }

            try {
                const status = await EmgService.getDeviceStatus(DEFAULT_DEVICE_ID);
                this.sensorsOnline = status.is_online;

                // "is_online" solo dice que la ESP32 responde por USB. Cada
                // canal se marca activo solo si el backend confirmo que ESE
                // canal en particular esta mandando datos reales
                // (channels_live), no porque el puerto serie este abierto.
                // Asi "3/3 Activas" deja de mentir cuando en realidad hay un
                // solo electrodo conectado (los otros dos siempre en 0.0).
                const liveCount = status.channels_live ?? 0;
                this.emgSignals = this.emgSignals.map((s, idx) => ({
                    ...s,
                    status: idx < liveCount ? "active" : "inactive",
                }));

                // El backend nunca abre el puerto serie solo: alguna pantalla
                // tiene que pedirlo. Ni la vista del doctor ni la del paciente
                // supervisado lo hacían (solo "Entrenamiento Libre"), asi que
                // el doctor se quedaba viendo "0/3" aunque el ESP32 estuviera
                // conectado. Reintento silencioso en cada sondeo, igual que
                // PatientFreeView.vue.
                if (!status.is_online) {
                    try {
                        await EmgService.connect();
                    } catch {
                        /* sin dispositivo o puerto ocupado: seguimos sondeando */
                    }
                }
            } catch {
                const off: EmgSignal["status"] = "inactive";
                this.sensorsOnline = false;
                this.emgSignals = this.emgSignals.map((s) => ({ ...s, status: off }));
            }
        },

        startSensorPolling(intervalMs = 1500) {
            this.refreshSensors();
            this.stopSensorPolling();
            sensorPollId = window.setInterval(() => this.refreshSensors(), intervalMs);
        },

        stopSensorPolling() {
            if (sensorPollId !== null) {
                clearInterval(sensorPollId);
                sensorPollId = null;
            }
        },
    },
});

// Recursos fuera del state reactivo (no deben serializarse ni observarse).
let liveSocket: WebSocket | null = null;
let sensorPollId: number | null = null;
