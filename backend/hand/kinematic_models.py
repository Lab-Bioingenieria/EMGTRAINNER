"""
Modelo cinemático de la mano robótica de 13 motores.
- Índice a meñique: MCP + PIP acoplados
- Pulgar: 3 GDL
- Muñeca: 2 GDL
"""
from dataclasses import dataclass
from typing import Dict

def clamp(v: float, vmin: float, vmax: float) -> float:
    return max(vmin, min(v, vmax))

# DEDO MCP–PIP ACOPLADO

@dataclass
class CoupledFinger2DOF:
    mcp_id: int
    pip_id: int

    k_pip: float = 0.65  # relación mecánica MCP - PIP

    mcp_min: float = 0.0
    mcp_max: float = 90.0
    pip_min: float = 0.0
    pip_max: float = 90.0

    def compute(self, mcp_angle: float) -> Dict[int, float]:
        mcp = clamp(mcp_angle, self.mcp_min, self.mcp_max)
        pip = clamp(self.k_pip * mcp, self.pip_min, self.pip_max)

        return {
            self.mcp_id: mcp,
            self.pip_id: pip,
        }

# PULGAR 3 GDL
@dataclass
class Thumb3DOF:
    cmc_opposition: int
    cmc_rotation: int
    mcp_flexion: int

    def compute(self, cmd: Dict[str, float]) -> Dict[int, float]:
        return {
            self.cmc_opposition: clamp(cmd.get("opposition", 0), 0, 45),
            self.cmc_rotation: clamp(cmd.get("rotation", 0), -30, 30),
            self.mcp_flexion: clamp(cmd.get("flexion", 0), 0, 60),
        }

# MODELO GLOBAL DE MANO
class HandKinematicModel:
    def __init__(self, handedness: int = +1):
        self.handedness = handedness
        self.fingers: Dict[str, CoupledFinger2DOF] = {}
        self.thumb: Thumb3DOF | None = None

    def add_finger(self, name: str, finger: CoupledFinger2DOF):
        self.fingers[name] = finger

    def set_thumb(self, thumb: Thumb3DOF):
        self.thumb = thumb

    def compute_pose(self, command: Dict) -> Dict[int, float]:
        motor_angles: Dict[int, float] = {}

        # Dedos índice a meñique
        for name, angle in command.get("fingers", {}).items():
            if name in self.fingers:
                res = self.fingers[name].compute(angle)
                for mid, val in res.items():
                    motor_angles[mid] = self.handedness * val

        # Pulgar
        if self.thumb and "thumb" in command:
            res = self.thumb.compute(command["thumb"])
            for mid, val in res.items():
                motor_angles[mid] = self.handedness * val

        return motor_angles
