import time
from typing import Dict
from core.dynamixel_interface import DynamixelInterface
from models.hand_profiles import HandProfile, MotorConfig
from models.hand_profiles import apply_hand_orientation


def move_finger_sequential(dx: DynamixelInterface, profile: HandProfile, finger_name: str, target_angles: Dict[str, float], delay_s: float = 0.15,):
    "Mueve un dedo motor por motor de forma secuencial (anti-colisión)"

    finger = profile.fingers[finger_name]

    for joint_name, target_deg in target_angles.items():
        motor: MotorConfig = finger.motors[joint_name]

        if motor.locked:
            continue

        # Aplicar orientación derecha o izquierda
        oriented_deg = apply_hand_orientation(target_deg, motor, profile.side,)

        # Limitar por rango mecánico
        safe_deg = max(motor.min_deg, min(motor.max_deg, oriented_deg))

        current_limit_units = int(motor.max_current_a / dx.CURRENT_UNIT_TO_AMP)
        dx.set_current_limit(motor.motor_id, current_limit_units)

        dx.move_motor_safe(motor.motor_id, dx.degrees_to_ticks_centered(safe_deg),)

        time.sleep(delay_s)
