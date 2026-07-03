import time
import os
from pathlib import Path
from datetime import datetime
from typing import Dict

from app.utils.physics import (current_to_torque_nm, torque_to_fingertip_force, total_grip_force,)
from app.utils.anthropometry import get_finger_length_m
from app.services.hand_service import HandService
from app.core.dynamixel_interface import DynamixelInterface

class TrainingSession:
    "Ejecuta una sesión clínica completa de entrenamiento"

    def __init__(self, config: Dict):
        self.config = config

        self.session_id = self._generate_session_id()
        self.session_path = self._create_session_folder()

        self.hand_service = HandService()
        self.profile_name = config["hand_profile"]
        self.gestures = config["gestures"]
        self.gesture_duration = config.get("gesture_duration", 5.0)
        self.rest_time = config.get("rest_time", 2.0)

    # Ejecución
    
    def run(self):
        self.hand_service.initialize_hand(self.profile_name)

        for gesture in self.gestures:
            self._execute_gesture_block(gesture)

    # Gesto
    def _execute_gesture_block(self, gesture_name: str):
        print(f"[SESSION] - Gesto: {gesture_name}")

        self.hand_service.execute_gesture(gesture_name)

        start = time.time()
        while time.time() - start < self.gesture_duration:
            self._record_metrics(gesture_name)
            time.sleep(0.25)

        time.sleep(self.rest_time)

    # Métricas
    def _record_metrics(self, gesture_name: str):
        dx = self.hand_service.dx
        profile = self.hand_service.profile

        if profile is None:
            raise RuntimeError("[ERROR] - Perfil de mano no inicializado")

        timestamp = time.time()
        finger_forces = {}

        for finger_name, finger in profile.fingers.items():
            for motor in finger.motors.values():

                if motor.locked:
                    continue
                
                try:
                    current_A = dx.read_current_amps(motor.motor_id)
                except Exception as e:
                    print(f"[WARN] Error leyendo motor {motor.motor_id}: {e}")
                    continue

                torque_nm = current_to_torque_nm(current_A)
                lever_arm = get_finger_length_m(finger_name)
                force_n = torque_to_fingertip_force(torque_nm, lever_arm)
                
                finger_forces.setdefault(finger_name, 0.0)
                finger_forces[finger_name] += force_n

                self._log_metric(timestamp, gesture_name, finger_name, motor.motor_id, current_A, torque_nm,force_n,)

        total_force = total_grip_force(finger_forces)
        print(f"[METRIC] - Fuerza total = {total_force:.2f} N")

    # Registro
    def _log_metric(self, ts, gesture, finger, motor, current, torque, force):
        with open(self.session_path / "metrics.csv", "a") as f:
            f.write(
                f"{ts},{gesture},{finger},{motor},"
                f"{current:.4f},{torque:.4f},{force:.2f}\n"
            )

    # Utilidades
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _create_session_folder(self) -> Path:
        path = Path("data/sessions") / self.session_id
        path.mkdir(parents=True, exist_ok=True)

        with open(path / "metrics.csv", "w") as f:
            f.write(
                "timestamp,gesture,finger,motor_id,"
                "current_A,torque_Nm,force_N\n"
            )

        return path
