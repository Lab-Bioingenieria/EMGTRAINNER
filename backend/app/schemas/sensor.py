from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class SensorStatus(BaseModel):
    sensor_name: str
    state: str # connected, disconnected, error
    details: Optional[str] = None

    class Config:
        from_attributes = True
