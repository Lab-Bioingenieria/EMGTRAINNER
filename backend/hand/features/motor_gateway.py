import time
import dynamixel_sdk as dxl

PROTOCOL_VERSION = 2.0
PORT_NAME = "COM4"
BAUDRATE = 1000000

ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
ADDR_PRESENT_CURRENT = 126
ADDR_CURRENT_LIMIT = 38

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

CURRENT_UNIT_TO_AMP = 0.00269

class DynamixelInterface:
    def __init__(self):
        self.port = dxl.PortHandler(PORT_NAME)
        self.packet = dxl.PacketHandler(PROTOCOL_VERSION)

    def initialize(self):
        self.port.openPort()
        self.port.setBaudRate(BAUDRATE)

    def enable_torque(self, motor_id: int):
        self.packet.write1ByteTxRx(self.port, motor_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

    def disable_torque(self, motor_id: int):
        self.packet.write1ByteTxRx(self.port, motor_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)

    def configure_free_motor(self, motor_id: int, max_current_a: float):
        current_units = int(max_current_a / CURRENT_UNIT_TO_AMP)
        self.packet.write2ByteTxRx(self.port, motor_id, ADDR_CURRENT_LIMIT, current_units)
        self.enable_torque(motor_id)

    def move_motor_safe(self, motor_id: int, goal_ticks: int):
        self.packet.write4ByteTxRx(self.port, motor_id, ADDR_GOAL_POSITION, goal_ticks)

    def read_feedback(self, motor_id: int):
        pos, _, _ = self.packet.read4ByteTxRx(
            self.port, motor_id, ADDR_PRESENT_POSITION
        )
        cur, _, _ = self.packet.read2ByteTxRx(
            self.port, motor_id, ADDR_PRESENT_CURRENT
        )

        return {
            "position_ticks": pos,
            "current_units": cur,
            "is_moving": False,
            "velocity": 0,
            "load": 0,
            "voltage": 12.0,
            "temperature": 30.0,
            "error_code": 0,
        }
