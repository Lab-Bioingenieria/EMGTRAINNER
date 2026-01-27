import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from models import GESTURES
from models import HandProfile, MotorConfig, apply_hand_orientation
from core import DynamixelInterface


logger = logging.getLogger(__name__)

@dataclass
class MotorFeedback:
    motor_id: int
    position_ticks: int
    position_deg: float
    velocity: int
    load: int
    voltage: float
    temperature: float
    is_moving: bool
    error_code: int


@dataclass
class HandStatus:
    timestamp: float
    motors_ok: int
    motors_error: int
    avg_voltage: float
    max_temperature: float
    all_healthy: bool
    error_messages: List[str]


class DynamixelError(Exception):
    pass


# ============================================================
# CONTROLLER
# ============================================================

class ProstheticController:
    def __init__(self, hand: HandProfile, dxl: DynamixelInterface):
        self.hand = hand
        self.dxl = dxl
        self.last_feedback: Dict[int, MotorFeedback] = {}
        self.max_retries = 3
        self.retry_delay = 0.1

    # --------------------------------------------------------
    # UTILIDADES
    # --------------------------------------------------------

    @staticmethod
    def clamp(value: float, min_v: float, max_v: float) -> float:
        return max(min_v, min(max_v, value))

    def deg_to_ticks_xl330(self, deg: float) -> int:
        return int(2048 + (deg / 360.0) * 4096)

    def ticks_to_deg_xl330(self, ticks: int) -> float:
        return ((ticks - 2048) / 4096.0) * 360.0

    # --------------------------------------------------------
    # INIT
    # --------------------------------------------------------

    def initialize_hand(self):
        logger.info(f"Inicializando mano: {self.hand.name}")

        for finger in self.hand.fingers.values():
            for motor in finger.motors.values():
                if motor.locked:
                    self.dxl.disable_torque(motor.motor_id)
                else:
                    self.dxl.configure_free_motor(
                        motor.motor_id,
                        motor.max_current_a
                    )

    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------

    def validate_gesture(self, gesture_name: str) -> bool:
        return (
            gesture_name in GESTURES and
            self.hand.name in GESTURES[gesture_name]
        )

    # --------------------------------------------------------
    # FEEDBACK
    # --------------------------------------------------------

    def get_motor_status(self, motor_id: int) -> Optional[MotorFeedback]:
        raw = self.dxl.read_feedback(motor_id)
        if raw is None:
            return None

        feedback = MotorFeedback(
            motor_id=motor_id,
            position_ticks=raw["position_ticks"],
            position_deg=self.ticks_to_deg_xl330(raw["position_ticks"]),
            velocity=raw["velocity"],
            load=raw["load"],
            voltage=raw["voltage"],
            temperature=raw["temperature"],
            is_moving=raw["is_moving"],
            error_code=raw["error_code"],
        )

        self.last_feedback[motor_id] = feedback
        return feedback

    def get_all_motor_status(self) -> Dict[int, MotorFeedback]:
        status = {}
        for finger in self.hand.fingers.values():
            for motor in finger.motors.values():
                if not motor.locked:
                    fb = self.get_motor_status(motor.motor_id)
                    if fb:
                        status[motor.motor_id] = fb
        return status

    # --------------------------------------------------------
    # GESTOS
    # --------------------------------------------------------

    def execute_gesture(self, gesture_name: str,
                        duration: float = 1.0,
                        wait_completion: bool = True) -> bool:

        if not self.validate_gesture(gesture_name):
            logger.error(f"Gesto inválido: {gesture_name}")
            return False

        gesture = GESTURES[gesture_name][self.hand.name]
        motor_ids = []

        try:
            for finger_name, joints in gesture.items():
                if finger_name not in self.hand.fingers:
                    continue

                finger = self.hand.fingers[finger_name]

                for joint, target_deg in joints.items():
                    if joint not in finger.motors:
                        continue

                    motor = finger.motors[joint]
                    if motor.locked:
                        continue

                    angle = apply_hand_orientation(
                        target_deg, motor, self.hand.side
                    )
                    angle = self.clamp(angle, motor.min_deg, motor.max_deg)

                    ticks = self.deg_to_ticks_xl330(angle)
                    self._move_motor_with_retry(motor.motor_id, ticks)
                    motor_ids.append(motor.motor_id)

            if wait_completion:
                self.wait_for_motors(motor_ids)

            time.sleep(duration)
            return True

        except Exception as e:
            logger.error(f"Error en gesto {gesture_name}: {e}")
            return False

    # --------------------------------------------------------
    # SECUENCIAS 
    # --------------------------------------------------------

    def execute_sequence(self,
                         gesture_list: List[str],
                         delays: Optional[List[float]] = None,
                         stop_on_error: bool = True) -> List[bool]:

        if delays is None:
            delays = [1.0] * len(gesture_list)

        results = []

        for i, (gesture, delay) in enumerate(zip(gesture_list, delays)):
            ok = self.execute_gesture(gesture, duration=delay)
            results.append(ok)

            if not ok and stop_on_error:
                break

            if i < len(gesture_list) - 1:
                time.sleep(delay)

        return results

    # --------------------------------------------------------
    # NEUTRAL
    # --------------------------------------------------------

    def move_to_default(self):
        for finger in self.hand.fingers.values():
            for motor in finger.motors.values():
                if motor.locked:
                    continue

                angle = apply_hand_orientation(
                    motor.default_deg, motor, self.hand.side
                )
                angle = self.clamp(angle, motor.min_deg, motor.max_deg)
                ticks = self.deg_to_ticks_xl330(angle)

                self._move_motor_with_retry(motor.motor_id, ticks)

    # --------------------------------------------------------
    # LOW LEVEL
    # --------------------------------------------------------

    def _move_motor_with_retry(self, motor_id: int, goal_ticks: int):
        for _ in range(self.max_retries):
            try:
                self.dxl.move_motor_safe(motor_id, goal_ticks)
                return
            except Exception:
                time.sleep(self.retry_delay)
        raise DynamixelError(f"Motor {motor_id} no respondió")

    def wait_for_motors(self, motor_ids: List[int], timeout: float = 5.0):
        start = time.time()
        while time.time() - start < timeout:
            if all(
                not self.get_motor_status(mid).is_moving
                for mid in motor_ids
            ):
                return True
            time.sleep(0.05)
        return False

    # --------------------------------------------------------
    # EMERGENCIA
    # --------------------------------------------------------

    def emergency_stop(self):
        for finger in self.hand.fingers.values():
            for motor in finger.motors.values():
                self.dxl.disable_torque(motor.motor_id)
