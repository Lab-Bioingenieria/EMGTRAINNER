from dataclasses import dataclass
from typing import Dict, List

@dataclass
class FingerProfile:
    motor_ids: List[int]
    open_deg: float
    close_deg: float
    max_current_a: float
    velocity: int

@dataclass
class HandProfile:
    name: str
    fingers: Dict[str, FingerProfile]
    sequence: List[str]   # Orden Anti-colisión

# PERFIL: MANO 6 GDL – MULTI-GESTO
SIX_DOF_HAND = HandProfile(
    name="six_dof_prosthesis",
    sequence=["index", "middle", "ring", "pinky", "thumb"], #"wrist"
    fingers={
        "index": FingerProfile(motor_ids=[4, 5],    open_deg=-10, close_deg=90, max_current_a=0.45,  velocity=20,),
        "middle": FingerProfile(motor_ids=[6, 7],   open_deg=-10, close_deg=90, max_current_a=0.45,  velocity=20,),
        "ring": FingerProfile( motor_ids=[8, 9],    open_deg=-10, close_deg=90, max_current_a=0.45,  velocity=20,),
        "pinky": FingerProfile(motor_ids=[10, 11],  open_deg=-10, close_deg=90, max_current_a=0.45,  velocity=20,),
        "thumb": FingerProfile(motor_ids=[1, 2, 3], open_deg=0,   close_deg=45, max_current_a=0.50,  velocity=15,),
        #"wrist": FingerProfile(motor_ids=[12, 13],  open_deg=0, close_deg=30, max_current_a=0.6,  velocity=12,),
    }
)
