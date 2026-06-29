from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HandProfileBase(BaseModel):
    name: str
    side: str  # "RIGHT" or "LEFT"


class HandProfileCreate(HandProfileBase):
    pass


class HandProfileRead(HandProfileBase):
    is_initialized: bool = False
    
    class Config:
        from_attributes = True


class GestureExecute(BaseModel):
    gesture_name: str
    profile_name: Optional[str] = None


class GestureResponse(BaseModel):
    gesture_name: str
    status: str
    message: Optional[str] = None


class TrainingSessionConfig(BaseModel):
    hand_profile: str
    gestures: List[str]
    gesture_duration: float = 5.0
    rest_time: float = 2.0


class SessionStartRequest(BaseModel):
    config: TrainingSessionConfig


class SessionResponse(BaseModel):
    session_id: str
    status: str
    profile_name: str
    gestures: List[str]


class MotorStatus(BaseModel):
    motor_id: int
    current_position: int
    current_amps: float
    is_enabled: bool


class HandStatusResponse(BaseModel):
    is_initialized: bool
    profile_name: Optional[str] = None
    detected_motors: List[int] = []
    motors_status: List[MotorStatus] = []
