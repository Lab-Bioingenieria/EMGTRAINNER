import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from hand.core.dynamixel_interface import DynamixelInterface
from hand.control.hand_controller import (initialize_hand_profile, execute_gesture,)
from hand.models.hand_profiles import HAND_PROFILES, HandProfile
from hand.core.physics import (current_to_torque_nm, torque_to_fingertip_force, total_grip_force,)
from hand.models.anthropometry import get_finger_length_m


class TrainingSession:
    "Ejecuta una sesión clínica completa configurada desde el frontend"

    def __init__(self, config: Dict):
        self.config = config
        self.session_id = self._generate_session_id()
        self.session_path = self._create_session_folder()

        profile_name = config["hand_profile"]

        if profile_name not in HAND_PROFILES:
            raise ValueError(f"Perfil de mano no reconocido: {profile_name}")

        self.hand_profile: HandProfile = HAND_PROFILES[profile_name]
        self.gestures = config["gestures"]
        self.gesture_duration = config["gesture_duration"]
        self.rest_time = config["rest_time"]

        self.dx = DynamixelInterface(port_name=config.get("port", "COM4"))

    # Inicialización
    
    def initialize(self):
        self.dx.initialize()
        self.dx.scan_motors()
        initialize_hand_profile(self.dx, self.hand_profile)

    # Ejecución de sesión
    
    def run(self):
        self.initialize()

        for gesture in self.gestures:
            self._execute_gesture_block(gesture)

    # Gesto individual
    
    def _execute_gesture_block(self, gesture_name: str):
        print(f"[SESSION] - Ejecutando gesto: {gesture_name}")

        execute_gesture(self.dx, self.hand_profile, gesture_name)

        start = time.time()

        while time.time() - start < self.gesture_duration:
            self._record_metrics(gesture_name)
            time.sleep(0.25)

        time.sleep(self.rest_time)

    # Métricas
   
    def _record_metrics(self, gesture_name: str):
        timestamp = time.time()
        finger_forces = {}

        for finger_name, finger in self.hand_profile.fingers.items():
            for motor in finger.motors.values():
                if motor.locked:
                    continue

                current_A = self.dx.read_current_amps(motor.motor_id)
                torque_nm = current_to_torque_nm(current_A)

                lever_arm = get_finger_length_m(finger_name)
                force_n = torque_to_fingertip_force(torque_nm, lever_arm)

                finger_forces.setdefault(finger_name, 0.0)
                finger_forces[finger_name] += force_n

                self._log_metric(timestamp, gesture_name, finger_name,  motor.motor_id, current_A, torque_nm, force_n,)

        total_force = total_grip_force(finger_forces)
        print(f"[METRIC] Fuerza total: {total_force:.2f} N")

    # Registro
    
    def _log_metric(self, timestamp, gesture, finger, motor_id, current, torque, force,):
        with open(self.session_path / "metrics.csv", "a") as f:
            f.write(
                f"{timestamp},{gesture},{finger},{motor_id},"
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
