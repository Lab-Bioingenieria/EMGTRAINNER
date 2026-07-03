from app.core.dynamixel_interface import DynamixelInterface
import time
import os
import glob

TEST_MOTOR_ID = 10
DELTA_DEG = 80

def find_u2d2_port():
    env_port = os.getenv("DYNAMIXEL_PORT")
    if env_port and os.path.exists(env_port):
        return env_port

    candidates = glob.glob("/dev/serial/by-id/*FTDI*")
    if candidates:
        return candidates[0]

    usb = glob.glob("/dev/ttyUSB*")
    if usb:
        return usb[0]

    return None

def main():
    port = find_u2d2_port()
    if not port:
        print("[ERROR] U2D2 no detectado. Conecta el dispositivo.")
        return 1

    print("[INFO] Usando puerto:", port)

    dx = DynamixelInterface(port_name=port)
    dx.initialize()
    dx.scan_motors()

    print("\n[TEST] - Leyendo posición inicial...")
    initial_pos = dx.read_position(TEST_MOTOR_ID)
    print("Posición inicial (ticks):", initial_pos)

    delta_ticks = dx.degrees_to_ticks_centered(DELTA_DEG) - 2048
    target_pos = initial_pos + delta_ticks

    print("[TEST] - Moviendo motor {} +{}°".format(TEST_MOTOR_ID, DELTA_DEG))
    dx.move_motor_safe(motor_id=TEST_MOTOR_ID, goal_position=target_pos)

    time.sleep(1)

    print("[TEST] - Retornando a posición inicial")
    dx.move_motor_safe(motor_id=TEST_MOTOR_ID, goal_position=initial_pos)

    print("[OK] - Prueba completada con éxito")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
