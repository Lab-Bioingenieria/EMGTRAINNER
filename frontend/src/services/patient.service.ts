import api from "@/lib/api";

export interface OrderCreate {
    device_id: string;
    requested_duration?: number;
    sample_rate?: number;
    signal_types?: string[];
    notes?: string;
}

export interface OrderRead {
    id: string;
    device_id: string;
    status: string;
    created_at: string;
    started_at?: string;
    finished_at?: string;
}

export interface PatientRead {
    id: number;
    patient_code: string;
    name: string;
    age: number;
    sessions_count: number;
    last_session: string | null;
    progress: number;
    status: string;
    created_at: string;
    updated_at: string;
}

export interface PatientCreate {
    patient_code: string;
    name: string;
    age: number;
    status?: string;
}

export class PatientService {
    static async getPatients(): Promise<PatientRead[]> {
        const response = await api.get("/patients/");
        return response.data;
    }

    static async createPatient(patient: PatientCreate): Promise<PatientRead> {
        const response = await api.post("/patients/", patient);
        return response.data;
    }

    static async createOrder(order: OrderCreate): Promise<OrderRead> {
        const response = await api.post("/orders", order);
        return response.data;
    }

    static async getOrder(orderId: string): Promise<OrderRead> {
        const response = await api.get(`/orders/${orderId}`);
        return response.data;
    }

    static async getPendingOrder(deviceId: string): Promise<OrderRead | null> {
        try {
            const response = await api.get(`/orders/pending?device_id=${deviceId}`);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.status === 404) {
                return null;
            }
            throw error;
        }
    }

    static async startOrder(orderId: string): Promise<OrderRead> {
        const response = await api.post(`/orders/${orderId}/start`);
        return response.data;
    }

    static async finishOrder(orderId: string): Promise<OrderRead> {
        const response = await api.post(`/orders/${orderId}/finish`);
        return response.data;
    }
}
