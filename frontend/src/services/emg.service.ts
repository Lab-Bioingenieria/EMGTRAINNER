import api from "@/lib/api";

export interface DeviceStatus {
    id: string;
    is_online: boolean;
    last_heartbeat: string;
    battery_level: number;
    wifi_signal_strength: number;
}

export class EmgService {
    static async getDeviceStatus(deviceId: string): Promise<DeviceStatus> {
        try {
            const response = await api.get(`/devices/${deviceId}/status`);
            return response.data;
        } catch (error) {
            console.error(`Failed to get status for device ${deviceId}`, error);
            // Return offline status/defaults on error to prevent UI crash
            return {
                id: deviceId,
                is_online: false,
                last_heartbeat: "",
                battery_level: 0,
                wifi_signal_strength: 0
            };
        }
    }
}
