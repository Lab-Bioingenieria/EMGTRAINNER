from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SensorStatus(BaseModel):
    sensor_name: str
    state: str # connected, disconnected, error
    details: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
