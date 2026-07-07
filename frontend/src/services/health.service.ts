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

export interface HardwareConfig {
    main_port: string | null;
    independent_data_acquisition: boolean;
    data_port: string | null;
    sensor_type: string;
    motor_type: string;
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

    static async getConfig(): Promise<HardwareConfig> {
        try {
            const response = await api.get('/microcontrollers/health_micro/config');
            return response.data;
        } catch (error) {
            console.error('Failed to get hardware config', error);
            return { main_port: null, independent_data_acquisition: false, data_port: null, sensor_type: 'umyo', motor_type: 'dynamixels' };
        }
    }

    static async updateConfig(config: HardwareConfig): Promise<HardwareConfig> {
        try {
            const response = await api.post('/microcontrollers/health_micro/config', config);
            return response.data;
        } catch (error) {
            console.error('Failed to update hardware config', error);
            throw error;
        }
    }
}
