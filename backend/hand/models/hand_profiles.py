from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Literal, Set
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

    # Ejemplo: [["index","middle","ring","pinky"], ["thumb"]]
    execution_groups: List[List[str]] = field(default_factory=list)

    all_fingers_simultaneous_gestures: Set[str] = field(default_factory=set)


# Utilidades

def apply_hand_orientation(angle: float, motor: MotorConfig, side: HandSide):
    if motor.inverted:
        return -angle
    if side == "LEFT":
        return -angle
    return angle

# Perfiles de Protesis

ELEVEN_DOF_RIGHT = HandProfile(
    name="Eleven_DOF_Right",
    side="RIGHT",
    locked_motors=[12, 13],
    execution_groups=[["index", "middle", "ring", "pinky"], ["thumb"]],
    all_fingers_simultaneous_gestures={"LIKE", "REST", "OPEN"},
    fingers={
        "thumb": FingerProfile(
            "thumb",
            motors={
                "MCP_FE": MotorConfig(1, 0, 120, 0, 0.8),
                "CMC_AA": MotorConfig(2, 0, 110, 0, 0.8),
                "CMC_FE": MotorConfig(3, 0, 45, 0, 0.8),
            },
        ),
        "index": FingerProfile(
            "index",
            motors={
                "PIP": MotorConfig(4, 0, 90, 0, 0.8),
                "MCP": MotorConfig(5, 0, 90, 0, 0.8),
            },
        ),
        "middle": FingerProfile(
            "middle",
            motors={
                "PIP": MotorConfig(6, 0, 90, 0, 0.8),
                "MCP": MotorConfig(7, 0, 90, 0, 0.8),
            },
        ),
        "ring": FingerProfile(
            "ring",
            motors={
                "PIP": MotorConfig(8, 0, 90, 0, 0.8),
                "MCP": MotorConfig(9, 0, 90, 0, 0.8),
            },
        ),
        "pinky": FingerProfile(
            "pinky",
            motors={
                "PIP": MotorConfig(10, 0, 90, 0, 0.8),
                "MCP": MotorConfig(11, 0, 90, 0, 0.8),
            },
        ),
    },
)


SIX_DOF_RIGHT = HandProfile(
    name="Six_DOF_Right",
    side="RIGHT",
    locked_motors=[3,12, 13],
    execution_groups=[["index", "middle", "ring", "pinky"], ["thumb"]],
    all_fingers_simultaneous_gestures={"LIKE", "REST", "OPEN"},
    fingers={
        "thumb": FingerProfile(
            "thumb",
            motors={
                "MCP_FE": MotorConfig(1, 0, 60, 30, 0.8),
                "CMC_AA": MotorConfig(2, 0, 60, 20, 0.8),
                "CMC_FE": MotorConfig(3, 0, 45, 0, 0.8, False, True),
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


TWO_DOF_LEFT = HandProfile(
    name="Two_DOF_Left",
    side="LEFT",
    locked_motors=[2, 3, 12, 13],
    fingers={
        "thumb": FingerProfile(
            "thumb",
            motors={
                "MCP_FE": MotorConfig(1, -50, 0, -10, 0.6),
                "CMC_AA": MotorConfig(2, -20, 20, -40, 0.5, inverted=True, locked=True),
                "CMC_FE": MotorConfig(3, 0, 0, 45, 0.5, locked=True),
            },
        ),
        "phalanx": FingerProfile(
            "phalanx",
            motors={
                f"{finger}_{joint}": MotorConfig(
                    motor_id=i,
                    min_deg=-45,
                    max_deg=0,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                )
                for i, (finger, joint) in enumerate(
                    [
                        ("II", "PIP"), ("II", "MCP"),
                        ("III", "PIP"), ("III", "MCP"),
                        ("IV", "PIP"), ("IV", "MCP"),
                        ("V", "PIP"), ("V", "MCP"),
                    ],
                    start=4,
                )
            },
        ),
    },
)


TWO_MOTORS = HandProfile(
    name="Two_Motors",
    side="RIGHT",
    locked_motors=[1,2,3,4,5,6,7,8,9,10,11,12,13],
    fingers={
        "phalanx": FingerProfile(
            "phalanx",
            motors={
                "14": MotorConfig(
                    motor_id=14,
                    min_deg=0,
                    max_deg=90,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                ),
                "15": MotorConfig(
                    motor_id=15,
                    min_deg=0,
                    max_deg=90,
                    default_deg=0,
                    max_current_a=0.5,
                    inverted=True,
                    locked=False,
                )
            },
        ),
    },
)

# Registro de Perfiles

HAND_PROFILES: Dict[str, HandProfile] = {
    ELEVEN_DOF_RIGHT.name: ELEVEN_DOF_RIGHT,
    SIX_DOF_RIGHT.name: SIX_DOF_RIGHT,
    TWO_DOF_LEFT.name: TWO_DOF_LEFT,
    TWO_MOTORS.name:   TWO_MOTORS,
}
