from hand.core.dynamixel_interface import DynamixelInterface
import time
import os

TEST_MOTOR_ID = 15          # Solo un motor
DELTA_DEG = 45              # movimiento pequeño

def main():
    port = os.getenv(
            "DYNAMIXEL_PORT",
            "/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTAO520W-if00-port0"
        )
    dx = DynamixelInterface(port_name=port)
    dx.initialize()
    dx.scan_motors()

    print("\n[TEST] - Leyendo posición inicial...")
    initial_pos = dx.read_position(TEST_MOTOR_ID)
    print(f"Posición inicial (ticks): {initial_pos}")

    # Converción de grados a ticks centrados
    delta_ticks = dx.degrees_to_ticks_centered(DELTA_DEG) - 2048
    target_pos = initial_pos + delta_ticks

    print(f"[TEST] - Moviendo motor {TEST_MOTOR_ID} +{DELTA_DEG}°")
    dx.move_motor_safe(motor_id=TEST_MOTOR_ID, goal_position=target_pos)

    time.sleep(1)

    print("[TEST] - Retornando a posición inicial")
    dx.move_motor_safe(motor_id=TEST_MOTOR_ID, goal_position=initial_pos)

    print("[OK] - Prueba completada con éxito")

if __name__ == "__main__":
    main()
