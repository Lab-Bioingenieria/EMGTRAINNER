from typing import Dict, List, Tuple

from app.schemas.hand_gestures import GESTURES
from app.schemas.hand_profiles import HandProfile, apply_hand_orientation, MotorConfig
from app.core.dynamixel_interface import DynamixelInterface, DEFAULT_PROFILE_VELOCITY, DEFAULT_PROFILE_ACCELERATION, POSITION_MODE

def initialize_hand_profile(dx: DynamixelInterface, profile: HandProfile):
    for finger in profile.fingers.values():
        for motor in finger.motors.values():
            if motor.locked:
                dx.lock_motor(motor.motor_id, motor.default_deg)
            else:
                dx.configure_free_motor(motor.motor_id, motor.max_current_a)

def _clamp(v: float, vmin: float, vmax: float) -> float:
    return max(vmin, min(vmax, v))

def _collect_targets_for_fingers(dx: DynamixelInterface,profile: HandProfile,gesture: Dict[str, Dict[str, float]],finger_names: List[str],) -> Tuple[Dict[int, int], Dict[int, float]]:
    """
    Retorna:
      targets: {motor_id: goal_ticks}
      current_limits: {motor_id: max_current_a}
    """
    targets: Dict[int, int] = {}
    current_limits: Dict[int, float] = {}

    for finger_name in finger_names:
        if finger_name not in gesture:
            continue
        if finger_name not in profile.fingers:
            continue

        finger = profile.fingers[finger_name]
        joints = gesture[finger_name]

        for joint_name, angle in joints.items():
            if joint_name not in finger.motors:
                continue

            motor: MotorConfig = finger.motors[joint_name]
            if motor.locked:
                continue

            oriented = apply_hand_orientation(angle, motor, profile.side)
            safe_deg = _clamp(oriented, motor.min_deg, motor.max_deg)

            targets[motor.motor_id] = dx.degrees_to_ticks_centered(safe_deg)
            current_limits[motor.motor_id] = motor.max_current_a

    return targets, current_limits

def _configure_motors_before_sync(dx: DynamixelInterface, current_limits: Dict[int, float]) -> None:

    for motor_id, max_a in current_limits.items():
        dx.set_operating_mode(motor_id, POSITION_MODE)

        units = dx.amps_to_current_units(max_a)
        dx.set_current_limit(motor_id, units)

        dx.set_profile_velocity(motor_id, DEFAULT_PROFILE_VELOCITY)
        dx.set_profile_acceleration(motor_id, DEFAULT_PROFILE_ACCELERATION)

        dx.enable_torque(motor_id)

def execute_gesture(dx: DynamixelInterface, profile: HandProfile, gesture_name: str) -> None:
    if gesture_name not in GESTURES:
        raise ValueError(f"[ERROR] - Gesto no definido: {gesture_name}")
    if profile.name not in GESTURES[gesture_name]:
        raise ValueError(
            f"[ERROR] - Gesto '{gesture_name}' no disponible para {profile.name}")

    gesture = GESTURES[gesture_name][profile.name]

      # Caso - Simultaneo
    if gesture_name in profile.all_fingers_simultaneous_gestures:
        finger_list = list(gesture.keys())  # los dedos que existan en ese gesto
        targets, current_limits = _collect_targets_for_fingers(dx, profile, gesture, finger_list)

        _configure_motors_before_sync(dx, current_limits)
        dx.move_motors_sync_safe(targets, timeout_s=1.0, current_limits_a=current_limits)
        return

    # Caso - 4 dedos simultáneo y luego pulgar - grupos definidos en el perfil
    groups = profile.execution_groups or [list(gesture.keys())]

    for group_fingers in groups:
        targets, current_limits = _collect_targets_for_fingers(dx, profile, gesture, group_fingers)

        if not targets:
            continue

        _configure_motors_before_sync(dx, current_limits)
        dx.move_motors_sync_safe(targets, timeout_s=1.0, current_limits_a=current_limits)
