from app.core.dynamixel_interface import DynamixelInterface, find_u2d2_port
import time

TEST_MOTOR_ID = 4
DELTA_DEG = 30

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

    delta_ticks = dx.degrees_to_ticks_centered(DELTA_DEG)
    target_pos = delta_ticks

    print("[TEST] - Moviendo motor {} +{}°".format(TEST_MOTOR_ID, DELTA_DEG))
    dx.move_motor_safe(motor_id=TEST_MOTOR_ID, goal_position=target_pos)

    print("[OK] - Prueba completada con éxito")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
