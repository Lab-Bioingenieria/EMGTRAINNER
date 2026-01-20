from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.schemas.sensor import SensorStatus

class DeviceBase(BaseModel):
    name: Optional[str] = None
    firmware_version: Optional[str] = None
    rssi: Optional[int] = None
    battery_level: Optional[float] = None

class DeviceCreate(DeviceBase):
    id: str # MAC address or specific ID
    api_key: str # Initial secret setup

class DeviceUpdate(DeviceBase):
    last_ip: Optional[str] = None

class DeviceRead(DeviceBase):
    id: str
    last_seen: Optional[datetime] = None
    is_online: bool
    sensors: List[SensorStatus] = []

    class Config:
        from_attributes = True

class HeartbeatRequest(BaseModel):
    device_id: str
    api_key: str
    sensors: Optional[List[SensorStatus]] = None
    battery_level: Optional[float] = None
    rssi: Optional[int] = None
    firmware_version: Optional[str] = None
