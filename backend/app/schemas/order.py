from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.schemas.datafile import DataFileRead

class OrderBase(BaseModel):
    requested_duration: Optional[int] = None
    sample_rate: Optional[int] = None
    signal_types: Optional[List[str]] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    device_id: str

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_reason: Optional[str] = None

class OrderRead(OrderBase):
    id: str
    device_id: str
    created_by: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_reason: Optional[str] = None
    data_files: List[DataFileRead] = []

    class Config:
        from_attributes = True
