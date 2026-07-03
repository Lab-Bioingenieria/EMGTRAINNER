from dataclasses import dataclass
from typing import Dict, List, Literal

HandSide = Literal["RIGHT", "LEFT"]

@dataclass
class MotorConfig:
    motor_id: int
    min_deg: float
    max_deg: float
    default_deg: float
    max_current_a: float
    inverted: bool = False
    locked: bool = False


@dataclass
class FingerProfile:
    name: str
    motors: Dict[str, MotorConfig]


@dataclass
class HandProfile:
    name: str
    side: HandSide
    fingers: Dict[str, FingerProfile]
    locked_motors: List[int]


def apply_hand_orientation(angle: float, motor: MotorConfig, side: HandSide) -> float:
    if motor.inverted:
        angle = -angle
    if side == "LEFT":
        angle = -angle
    return angle
