import time
from typing import Dict, List, Optional

from features.motion_math import clamp, deg_to_ticks_xl330, ticks_to_deg_xl330
from features.hand_models import HandProfile, MotorConfig, apply_hand_orientation
from features.gesture_library import GESTURES
from features.motor_gateway import DynamixelInterface
from features.motor_feedback import MotorFeedback


class DynamixelError(Exception):
    pass


class ProstheticController:
    def __init__(self, hand: HandProfile, dxl: DynamixelInterface):
        self.hand = hand
        self.dxl = dxl
        self.last_feedback: Dict[int, MotorFeedback] = {}
        self.max_retries = 3

    def initialize_hand(self):
        for finger in self.hand.fingers.values():
            for motor in finger.motors.values():
                if motor.locked:
                    self.dxl.disable_torque(motor.motor_id)
                else:
                    self.dxl.configure_free_motor(
                        motor.motor_id, motor.max_current_a
                    )

    def validate_gesture(self, name: str) -> bool:
        return name in GESTURES and self.hand.name in GESTURES[name]

    def get_motor_status(self, motor_id: int) -> Optional[MotorFeedback]:
        raw = self.dxl.read_feedback(motor_id)
        if not raw:
            return None

        fb = MotorFeedback(
            motor_id=motor_id,
            position_ticks=raw["position_ticks"],
            position_deg=ticks_to_deg_xl330(raw["position_ticks"]),
            velocity=raw["velocity"],
            load=raw["load"],
            voltage=raw["voltage"],
            temperature=raw["temperature"],
            is_moving=raw["is_moving"],
            error_code=raw["error_code"],
        )
        self.last_feedback[motor_id] = fb
        return fb

    def execute_gesture(self, gesture_name: str) -> bool:
        if not self.validate_gesture(gesture_name):
            return False

        gesture = GESTURES[gesture_name][self.hand.name]

        for finger_name, joints in gesture.items():
            if finger_name not in self.hand.fingers:
                continue

            finger = self.hand.fingers[finger_name]

            for joint, target_deg in joints.items():
                if joint not in finger.motors:
                    continue

                motor: MotorConfig = finger.motors[joint]
                if motor.locked:
                    continue

                angle = apply_hand_orientation(
                    target_deg, motor, self.hand.side
                )
                angle = clamp(angle, motor.min_deg, motor.max_deg)
                ticks = deg_to_ticks_xl330(angle)

                self._move_motor_with_retry(motor.motor_id, ticks)

        return True

    def _move_motor_with_retry(self, motor_id: int, goal_ticks: int):
        for _ in range(self.max_retries):
            try:
                self.dxl.move_motor_safe(motor_id, goal_ticks)
                return
            except Exception:
                time.sleep(0.1)
        raise DynamixelError(f"Motor {motor_id} no respondió")
