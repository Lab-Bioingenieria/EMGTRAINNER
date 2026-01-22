from ..models.gestures import GESTURES
from ..models.hand_profiles import HandProfile, apply_hand_orientation
from ..core.dynamixel_interface import DynamixelInterface

def initialize_hand_profile(dx: DynamixelInterface, profile: HandProfile):
    for finger in profile.fingers.values():
        for motor in finger.motors.values():
            if motor.locked:
                dx.lock_motor(motor.motor_id, motor.default_deg)
            else:
                dx.configure_free_motor(motor.motor_id, motor.max_current_a)

def execute_gesture(dx: DynamixelInterface, profile: HandProfile, gesture_name: str) -> None:
    if gesture_name not in GESTURES:
        raise ValueError(f"[ERROR] - Gesto no definido: {gesture_name}")
    if profile.name not in GESTURES[gesture_name]:
        raise ValueError(
            f"[ERROR] - Gesto '{gesture_name}' no disponible para {profile.name}")
    gesture = GESTURES[gesture_name][profile.name]

    for finger_name, joints in gesture.items():
        finger = profile.fingers[finger_name]

        for joint_name, angle in joints.items():
            motor = finger.motors[joint_name]

            if motor.locked:
                continue
            oriented_angle = apply_hand_orientation(angle, motor, profile.side)
            
            dx.move_motor_safe(motor.motor_id, dx.degrees_to_ticks_centered(oriented_angle))