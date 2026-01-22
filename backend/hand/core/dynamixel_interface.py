import time
from typing import List
import dynamixel_sdk as dxl

# CONFIGURACION GENERAL
PROTOCOL_VERSION = 2.0

DEFAULT_BAUDRATE = 1000000

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

# DIRECCIONES XL330
ADDR_OPERATING_MODE = 11
ADDR_TORQUE_ENABLE = 64
ADDR_CURRENT_LIMIT = 38
ADDR_PROFILE_ACCELERATION = 108
ADDR_PROFILE_VELOCITY = 112
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_CURRENT = 126
ADDR_PRESENT_POSITION = 132

POSITION_MODE = 3

# PARAMETROS DE SEGURIDAD
TORQUE_CONSTANT_NM_PER_AMP = 0.0011
MAX_CURRENT_A = 0.6               # limite seguro
DEFAULT_PROFILE_VELOCITY = 20
DEFAULT_PROFILE_ACCELERATION = 10

# GRUPOS DE MOTORES
MOTOR_GROUPS = {
    "thumb":  [1, 2, 3],
    "index":  [4, 5],
    "middle": [6, 7],
    "ring":   [8, 9],
    "pinky":  [10, 11],
    "wrist":  [12, 13],
}


# CLASE PRINCIPAL
class DynamixelInterface:
    CURRENT_UNIT_TO_AMP = 0.00269     # XL330 datasheet
    DEFAULT_CURRENT_LIMIT_UNITS = int(0.8 / CURRENT_UNIT_TO_AMP)  # =297
    
    def __init__(self, port_name: str, baudrate: int = DEFAULT_BAUDRATE):
        self.port_name = port_name
        self.baudrate = baudrate
        
        self.port_handler = dxl.PortHandler(port_name)
        self.packet_handler = dxl.PacketHandler(PROTOCOL_VERSION)
        self.detected_ids: List[int] = []

    # INICIALIZACION
    def initialize(self):
        if not self.port_handler.openPort():
            raise RuntimeError("[ERROR] - No se pudo abrir el puerto serie")

        if not self.port_handler.setBaudRate(self.baudrate):
            raise RuntimeError("[ERROR] - No se pudo configurar el baudrate")

        print(f"[OK] - Puerto {self.port_name} abierto a {self.baudrate} bps")

    def scan_motors(self, id_range=range(1, 16)) -> List[int]:
        self.detected_ids.clear()
        for motor_id in id_range:
            _, result, _ = self.packet_handler.ping(self.port_handler, motor_id)
            if result == dxl.COMM_SUCCESS:
                self.detected_ids.append(motor_id)
                print(f"[OK] - Motor detectado ID {motor_id}")
        return self.detected_ids

    # CONFIGURACION SEGURA
    def set_operating_mode(self, motor_id: int, mode: int):
        self.disable_torque(motor_id)
        self.packet_handler.write1ByteTxRx(self.port_handler, motor_id, ADDR_OPERATING_MODE, mode)

    def set_current_limit(self, motor_id: int, current_limit_units: int):
        self.packet_handler.write2ByteTxRx(self.port_handler, motor_id, ADDR_CURRENT_LIMIT, current_limit_units)

    def set_profile_velocity(self, motor_id: int, velocity: int):
        self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, ADDR_PROFILE_VELOCITY, velocity)

    def set_profile_acceleration(self, motor_id: int, acceleration: int):
        self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, ADDR_PROFILE_ACCELERATION, acceleration)

    # TORQUE
    def enable_torque(self, motor_id: int):
        self.packet_handler.write1ByteTxRx(self.port_handler, motor_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

    def disable_torque(self, motor_id: int):
        self.packet_handler.write1ByteTxRx(self.port_handler, motor_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)

    # LECTURA
    def read_position(self, motor_id: int) -> int:
        pos, _, _ = self.packet_handler.read4ByteTxRx(self.port_handler, motor_id, ADDR_PRESENT_POSITION)
        return pos

    def read_current_units(self, motor_id: int) -> int:
        raw, _, _ = self.packet_handler.read2ByteTxRx(self.port_handler, motor_id, ADDR_PRESENT_CURRENT)
        if raw > 32767:
            raw -= 65536
        return raw

    def read_current_amps(self, motor_id: int) -> float:
        current_units = self.read_current_units(motor_id)
        return abs(current_units) * self.CURRENT_UNIT_TO_AMP
    
    def amps_to_current_units(self, amps: float) -> int:
        return int(amps / self.CURRENT_UNIT_TO_AMP)

    # MOVIMIENTO SEGURO
    def move_motor_safe(self, motor_id: int, goal_position: int, timeout_s: float = 1.0):
        # Configuracion previa obligatoria
        self.set_operating_mode(motor_id, POSITION_MODE)
        self.set_current_limit(motor_id, self.DEFAULT_CURRENT_LIMIT_UNITS)
        self.set_profile_velocity(motor_id, DEFAULT_PROFILE_VELOCITY)
        self.set_profile_acceleration(motor_id, DEFAULT_PROFILE_ACCELERATION)
        self.enable_torque(motor_id)

        # Enviar posicion objetivo
        self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, ADDR_GOAL_POSITION, goal_position)

        start_time = time.time()
        stable_count = 0
        while time.time() - start_time < timeout_s:
            current_a = self.read_current_amps(motor_id)
            print(f"[DEBUG] - Motor {motor_id} corriente = {current_a:.2f} A")

            if current_a > MAX_CURRENT_A:
                stable_count += 1
                if stable_count >= 3:
                    self.disable_torque(motor_id)
                raise RuntimeError(
                    f"[WARNING] - Sobrecorriente detectada en motor {motor_id}: {current_a:.2f} A"
                )
            else:
                stable_count = 0

            time.sleep(0.05)

    # CONVERSIONES
    @staticmethod
    def degrees_to_ticks_centered(deg: float) -> int:
        return int(2048 + (deg / 360.0) * 4096)

    @staticmethod
    def current_to_torque(current_a: float) -> float:
        TORQUE_CONSTANT = 0.0011  # Nm/A (XL330)
        return current_a * TORQUE_CONSTANT
    
    def lock_motor(self, motor_id: int, angle_deg: float):
        pos = self.degrees_to_ticks_centered(angle_deg)
        self.enable_torque(motor_id)
        self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, ADDR_GOAL_POSITION, pos)

    def configure_free_motor(self, motor_id: int, max_current_a: float):
        current_units = int(max_current_a / self.CURRENT_UNIT_TO_AMP)
        self.set_current_limit(motor_id, current_units)
        self.enable_torque(motor_id)
    
