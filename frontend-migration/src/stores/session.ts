import { defineStore } from "pinia";
import type { Gesture, TrainingMode, EmgSignal } from "../lib/constants";
import { ALL_GESTURES } from "../lib/constants";

export const useSessionStore = defineStore("session", {
    state: () => ({
        sessionCode: "7891",
        trainingMode: null as TrainingMode | null,
        selectedGestures: [] as Gesture[],
        phase: "setup" as "setup" | "waiting" | "connected" | "running" | "paused" | "finished",
        emgSignals: [
            { id: 1, name: "Canal 1", status: "active" },
            { id: 2, name: "Canal 2", status: "active" },
            { id: 3, name: "Canal 3", status: "active" },
        ] as EmgSignal[],
        sessionTime: 0,
    }),
    actions: {
        setTrainingMode(mode: TrainingMode | null) {
            this.trainingMode = mode;
        },
        setSelectedGestures(gestures: Gesture[]) {
            this.selectedGestures = gestures;
        },
        setPhase(phase: "setup" | "waiting" | "connected" | "running" | "paused" | "finished") {
            this.phase = phase;
        },
        incrementTime() {
            this.sessionTime++;
        },
        resetSession() {
            this.phase = "setup";
            this.sessionTime = 0;
            this.trainingMode = null;
            this.selectedGestures = [];
        },
        generateNewCode() {
            // Simple random 4 digit
            this.sessionCode = Math.floor(1000 + Math.random() * 9000).toString();
        },
    },
});
