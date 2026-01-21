import api from "@/lib/api";

export interface PortInfo {
    port: string;
    description: string;
    hwid: string;
}

export interface HealthCheckResponse {
    count: number;
    ports: PortInfo[];
}

export class HealthService {
    static async checkPorts(): Promise<HealthCheckResponse> {
        try {
            const response = await api.get('/microcontrollers/health_micro/ports');
            return response.data;
        } catch (error) {
            console.error('Failed to check microcontroller ports', error);
            return { count: 0, ports: [] };
        }
    }
}
