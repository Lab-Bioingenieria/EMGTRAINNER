export type TrainingMode = "TLC" | "LLC";

export interface Gesture {
    id: string;
    name: string;
    nameEn: string;
}

export const ALL_GESTURES: Gesture[] = [
    { id: "1", name: "Palma Abajo", nameEn: "Palm Down" },
    { id: "2", name: "Palma Arriba", nameEn: "Palm Up" },
    { id: "3", name: "Cerrar Mano", nameEn: "Close Hand" },
    { id: "4", name: "Abrir Mano", nameEn: "Open Hand" },
    { id: "5", name: "Pinza Cerrada", nameEn: "Close Pinch" },
    { id: "6", name: "Pinza Abierta", nameEn: "Open Pinch" },
    { id: "7", name: "Mano en Reposo", nameEn: "Rest Hand" },
    { id: "8", name: "Apuntar con Índice", nameEn: "Point Index" },
];

export interface EmgSignal {
    id: number;
    name: string;
    status: "active" | "warning" | "inactive";
}

export const API_BASE_URL = "http://localhost:8000/v1";
export const DEFAULT_DEVICE_ID = "esp32-myo-1";

