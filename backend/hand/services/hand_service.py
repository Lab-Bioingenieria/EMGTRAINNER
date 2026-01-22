import os
from typing import Optional
from hand.core.dynamixel_interface import DynamixelInterface
from hand.control.hand_controller import initialize_hand_profile, execute_gesture
from hand.models.hand_profiles import HAND_PROFILES, HandProfile

class HandService:
  
    def __init__(self):
        # Puerto desde entorno (Docker / Jetson)
        port = os.getenv(
            "DYNAMIXEL_PORT",
            "/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTAO520W-if00-port0"
        )

        self.dx = DynamixelInterface(port_name=port)
        self.profile: Optional[HandProfile] = None
        self.initialized: bool = False

    # Inicialización
    def initialize_hand(self, profile_name: str):
        if profile_name not in HAND_PROFILES:
            raise ValueError(f"[ERROR] - Perfil de mano no válido: {profile_name}")

        self.profile = HAND_PROFILES[profile_name]

        self.dx.initialize()
        self.dx.scan_motors()
        initialize_hand_profile(self.dx, self.profile)

        self.initialized = True
        print(f"[HAND] - Perfil '{profile_name}' inicializado")

    # Gestos
    def execute_gesture(self, gesture_name: str):
        if not self.initialized or self.profile is None:
            raise RuntimeError("[ERROR] - La mano no ha sido inicializada")

        execute_gesture(self.dx, self.profile, gesture_name)

    # Estado
    def get_profile_name(self) -> str:
        return self.profile.name if self.profile else "NONE"
