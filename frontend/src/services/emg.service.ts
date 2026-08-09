import api from "@/lib/api";

export interface DeviceStatus {
    id: string;
    is_online: boolean;
    last_heartbeat: string;
    /** Null until the device firmware reports telemetry. Never fabricate a reading. */
    battery_level: number | null;
    wifi_signal_strength: number | null;
}

export class EmgService {
    static async getDeviceStatus(deviceId: string): Promise<DeviceStatus> {
        try {
            // Check real connection status from sensor service
            const response = await api.get('/monitoring/sensor/emg/status');
            const data = response.data;

            return {
                id: deviceId,
                is_online: data.connected,
                last_heartbeat: new Date().toISOString(),
                battery_level: data.battery_level ?? null,
                wifi_signal_strength: data.wifi_signal_strength ?? null
            };
        } catch (error) {
            console.error(`Failed to get status for device ${deviceId}`, error);
            // Return offline status/defaults on error to prevent UI crash
            return {
                id: deviceId,
                is_online: false,
                last_heartbeat: "",
                battery_level: null,
                wifi_signal_strength: null
            };
        }
    }
    static async startSession(category: string = "") {
        return api.post(`/monitoring/sensor/emg/start?category=${encodeURIComponent(category)}`);
    }

    static async stopSession() {
        return api.post('/monitoring/sensor/emg/stop');
    }

    static async getLatestSession() {
        try {
            const response = await api.get('/storage/sessions');
            return response.data.length > 0 ? response.data[0] : null;
        } catch (error) {
            console.error("Failed to get sessions", error);
            return null;
        }
    }

    static async setSessionInfo(name: string, age: string = "") {
        return api.post(`/monitoring/sensor/emg/session/info?name=${encodeURIComponent(name || 'Anonymous')}&age=${encodeURIComponent(age)}`);
    }

    static async setMovementLabel(label: string) {
        return api.post(`/monitoring/sensor/emg/label?label=${encodeURIComponent(label)}`);
    }

    static async getAllSessions() {
        const response = await api.get('/storage/sessions');
        return response.data;
    }

    static async connect() {
        return api.post('/monitoring/sensor/emg/connect');
    }
}
