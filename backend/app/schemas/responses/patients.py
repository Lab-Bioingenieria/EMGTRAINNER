from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PatientResponse(BaseModel):
    id: int
    patient_code: str
    name: str
    age: int
    sessions_count: int
    last_session: Optional[str]
    progress: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
