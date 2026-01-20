from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device, SensorStatus
from app.schemas.device import DeviceCreate, DeviceUpdate

class DeviceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, device_in: DeviceCreate) -> Device:
        device = Device(**device_in.dict())
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        return device

    async def get_by_id(self, device_id: str) -> Optional[Device]:
        query = select(Device).where(Device.id == device_id).options(selectinload(Device.sensors))
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_api_key(self, api_key: str) -> Optional[Device]:
        query = select(Device).where(Device.api_key == api_key)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update(self, device: Device, device_in: DeviceUpdate) -> Device:
        update_data = device_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(device, field, value)
        
        await self.session.commit()
        await self.session.refresh(device)
        return device
    
    async def update_heartbeat(self, device: Device, last_seen: str, is_online: bool) -> Device:
        device.last_seen = last_seen
        device.is_online = is_online
        await self.session.commit()
        await self.session.refresh(device)
        return device

    async def update_sensors(self, device_id: str, sensors_data: List[dict]):
        # Naive implementation: delete all and recreate, or update existing. 
        # For MVP, upsert logic or simple check is fine.
        # Let's try to find existing and update, or create new.
        
        for sensor_data in sensors_data:
            query = select(SensorStatus).where(
                SensorStatus.device_id == device_id,
                SensorStatus.sensor_name == sensor_data["sensor_name"]
            )
            result = await self.session.execute(query)
            sensor = result.scalars().first()
            
            if sensor:
                sensor.state = sensor_data["state"]
                sensor.details = sensor_data.get("details")
                sensor.last_seen = sensor_data.get("last_seen")
            else:
                new_sensor = SensorStatus(
                    device_id=device_id,
                    sensor_name=sensor_data["sensor_name"],
                    state=sensor_data["state"],
                    details=sensor_data.get("details"),
                    last_seen=sensor_data.get("last_seen")
                )
                self.session.add(new_sensor)
        
        await self.session.commit()
