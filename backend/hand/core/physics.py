from typing import Dict

# Constantes XL330
TORQUE_CONSTANT_NM_PER_AMP = 0.0011

def current_to_torque_nm(current_amp: float) -> float:
    return current_amp * TORQUE_CONSTANT_NM_PER_AMP


def torque_to_fingertip_force(torque_nm: float, lever_arm_m: float) -> float:
    """
    Fuerza en la yema del dedo -> F = τ / r
    """
    if lever_arm_m <= 0:
        raise ValueError("Brazo de palanca inválido")
    return torque_nm / lever_arm_m


def total_grip_force(finger_forces: Dict[str, float]) -> float:
    """
    Suma total de fuerza de agarre
    """
    return sum(finger_forces.values())
