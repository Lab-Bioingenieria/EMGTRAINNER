from pydantic import BaseModel
from typing import Dict, Literal


class JointEuler(BaseModel):
    x: float
    y: float
    z: float


class GestureEvent(BaseModel):
    ts: float
    gesture: str
    conf: float
    source: str | None = None


class JointState(BaseModel):
    ts: float
    gesture: str | None = None
    conf: float | None = None
    mode: Literal['POSE', 'NLA'] = 'NLA'
    joints: Dict[str, JointEuler] | None = None


class PlannedGesture(BaseModel):
    gesture: str
    play_mode: Literal['once', 'loop', 'hold'] = 'once'
    intermediate: list[str] | None = None
    joints: Dict[str, JointEuler] | None = None
