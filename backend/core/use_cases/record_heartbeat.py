from datetime import datetime, timedelta
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import HeartbeatRequest

class RecordHeartbeat:
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository

    async def execute(self, request: HeartbeatRequest):
        # Update device last_seen and online status
        # Note: In a real app we might validate API Key here or in middleware.
        # Assuming middleware handles auth or we check it here if needed.
        
        device = await self.device_repository.get_by_id(request.device_id)
        if not device:
            # Optionally create device on fly or raise error?
            # For MVP let's assume device must be preregistered or we auto-register if we had a registration flow.
            # But user said "Autenticación de dispositivo", so it implies it exists.
            raise ValueError("Device not found")

        if device.api_key != request.api_key:
             raise ValueError("Invalid API Key")

        # Update core device stats
        device.battery_level = request.battery_level
        device.rssi = request.rssi
        device.firmware_version = request.firmware_version
        
        # Mark as online
        await self.device_repository.update_heartbeat(device, last_seen=datetime.utcnow(), is_online=True)

        # Update sensors
        if request.sensors:
             # Convert schema to dict list for repository
             sensors_data = [s.dict() for s in request.sensors]
             # Add timestamps if not present
             for s in sensors_data:
                 if not s.get("last_seen"):
                     s["last_seen"] = datetime.utcnow()
            
             await self.device_repository.update_sensors(request.device_id, sensors_data)
        
        return {"status": "ok", "timestamp": datetime.utcnow()}
