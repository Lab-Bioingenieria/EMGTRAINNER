export type TrainingMode = "TLC" | "LLC";

export interface Gesture {
    id: string;
    name: string;
    nameEn: string;
}

export const ALL_GESTURES: Gesture[] = [
    { id: "1", name: "Puño Cerrado", nameEn: "Closure Hand" },
    { id: "2", name: "Mano Abierta", nameEn: "Open Hand" },
    { id: "3", name: "Flexión Muñeca", nameEn: "Wrist Flexion" },
    { id: "4", name: "Extensión Muñeca", nameEn: "Wrist Extension" },
    { id: "5", name: "Pinza Fina", nameEn: "Fine Pinch" },
    { id: "6", name: "No Gesto", nameEn: "No Gesture" },
];

export interface EmgSignal {
    id: number;
    name: string;
    status: "active" | "warning" | "inactive";
}
