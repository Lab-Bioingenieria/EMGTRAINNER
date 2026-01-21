from dataclasses import dataclass
from typing import Dict, List, Tuple, Literal
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

def apply_hand_orientation(angle: float, motor: MotorConfig, side: HandSide):
    if motor.inverted:
        return -angle
    if side == "LEFT":
        return -angle
    return angle


SIX_DOF_HAND = HandProfile(
    name="Six_DOF_Right",
    side="RIGHT",
    locked_motors=[12, 13],
    fingers={
        "thumb": FingerProfile(
            "thumb",
            motors={
                "MCP_FE": MotorConfig(1, 0, 60, 30, 0.8),
                "CMC_AA": MotorConfig(2, 0, 40, 20, 0.8),
                "CMC_FE": MotorConfig(3, 0, 70, 45, 0.8),
            },
        ),
        "index": FingerProfile(
            "index",
            motors={
                "PIP": MotorConfig(4, 0, 90, 45, 0.8),
                "MCP": MotorConfig(5, 0, 90, 30, 0.8),
            },
        ),
        "middle": FingerProfile(
            "middle",
            motors={
                "PIP": MotorConfig(6, 0, 90, 55, 0.8),
                "MCP": MotorConfig(7, 0, 90, 35, 0.8),
            },
        ),
        "ring": FingerProfile(
            "ring",
            motors={
                "PIP": MotorConfig(8, 0, 90, 45, 0.8),
                "MCP": MotorConfig(9, 0, 90, 40, 0.8),
            },
        ),
        "pinky": FingerProfile(
            "pinky",
            motors={
                "PIP": MotorConfig(10, 0, 90, 35, 0.8),
                "MCP": MotorConfig(11, 0, 90, 45, 0.8),
            },
        ),
    },
)


TWO_DOF_HAND = HandProfile(
    name="Two_DOF_Left",
    side="LEFT",
    locked_motors=[2, 3, 12, 13],
    fingers={
        "thumb": FingerProfile(
            "thumb",
            motors={
                "MCP_FE": MotorConfig(
                    motor_id=1,
                    min_deg=-50,
                    max_deg=0,
                    default_deg=-10,
                    max_current_a=0.6,
                    inverted=False,
                    locked=False,
                ),
                "CMC_AA": MotorConfig(
                    motor_id=2,
                    min_deg=-20,
                    max_deg=20,
                    default_deg=-40,
                    max_current_a=0.5,
                    inverted=True,
                    locked=True,
                ),
                "CMC_FE": MotorConfig(
                    motor_id=3,
                    min_deg=0,
                    max_deg=0,
                    default_deg=45,
                    max_current_a=0.5,
                    locked=True,
                ),
            },
        ),
        "phalanx": FingerProfile(
            "phalanx",
            motors={
                "II_PIP_FE": MotorConfig(
                    motor_id=4,
                    min_deg=-45,
                    max_deg=0,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                ),
                "II_MCP_FE": MotorConfig(
                    motor_id=5,
                    min_deg=-45,
                    max_deg=0,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                ),
                "III_PIP_FE": MotorConfig(
                    motor_id=6,
                    min_deg=-45,
                    max_deg=0,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                ),
                "III_MCP_FE": MotorConfig(
                    motor_id=7,
                    min_deg=-45,
                    max_deg=0,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                ),
                "IV_PIP_FE": MotorConfig(
                    motor_id=8,
                    min_deg=-45,
                    max_deg=0,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                ),
                "IV_MCP_FE": MotorConfig(
                    motor_id=9,
                    min_deg=-45,
                    max_deg=0,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                ),
                "V_PIP_FE": MotorConfig(
                    motor_id=10,
                    min_deg=-45,
                    max_deg=0,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                ),
                "V_MCP_FE": MotorConfig(
                    motor_id=11,
                    min_deg=-45,
                    max_deg=0,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                ),
            },
        ),
    },
)

