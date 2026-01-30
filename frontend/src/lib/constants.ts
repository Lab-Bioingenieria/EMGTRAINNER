export type TrainingMode = "TLC" | "LLC";

export interface Gesture {
    id: string;
    name: string;
    nameEn: string;
}

export const ALL_GESTURES: Gesture[] = [
    { id: "1", name: "Abrir", nameEn: "Open" },
    { id: "2", name: "Cerrar", nameEn: "Close" },
    { id: "3", name: "Like", nameEn: "Like" },
    { id: "4", name: "Apuntar", nameEn: "Point" },
    { id: "5", name: "Pinza", nameEn: "Pinch" },
    { id: "6", name: "Cilindrico", nameEn: "Cylindrical" },
    { id: "7", name: "Esférico", nameEn: "Spherical" },
];

export interface EmgSignal {
    id: number;
    name: string;
    status: "active" | "warning" | "inactive";
}

export const API_BASE_URL = "/v1";
export const DEFAULT_DEVICE_ID = "esp32-myo-1";

