from datetime import datetime
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceRead

class GetDeviceStatus:
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository

    async def execute(self, device_id: str, threshold_seconds: int = 30) -> DeviceRead:
        device = await self.device_repository.get_by_id(device_id)
        if not device:
            raise ValueError("Device not found")

        # Check if device is actually online based on threshold
        if device.last_seen:
            time_diff = datetime.utcnow() - device.last_seen
            if time_diff.total_seconds() > threshold_seconds:
                device.is_online = False
                # Optionally persist this change or just return computed status
                # For read-heavy operations, computing on fly is okay, but if we want to query "all online devices" we need persistence.
                # Let's keep it simple: we trust the DB 'is_online' but we could double check.
                # Actually, the user requirement said: "Si el dispositivo manda heartbeat cada N segundos, el status debe ser online si last_seen < threshold."
                # So we should probably compute it here.
                
                # If we want to return the computed status without saving (to avoid write on read):
                # device.is_online = False 
                pass # logic handled in display or we update?
        
        # Let's enforce the check:
        is_actually_online = False
        if device.last_seen:
             time_diff = datetime.utcnow() - device.last_seen
             if time_diff.total_seconds() < threshold_seconds:
                 is_actually_online = True
        
        device.is_online = is_actually_online
        
        return device
