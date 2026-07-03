from dataclasses import dataclass
from typing import List

@dataclass
class MotorFeedback:
    motor_id: int
    position_ticks: int
    position_deg: float
    velocity: int
    load: int
    voltage: float
    temperature: float
    is_moving: bool
    error_code: int


@dataclass
class HandStatus:
    motors_ok: int
    motors_error: int
    avg_voltage: float
    max_temperature: float
    all_healthy: bool
    error_messages: List[str]
