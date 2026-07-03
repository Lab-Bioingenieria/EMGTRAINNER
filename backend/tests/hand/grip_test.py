import os
import glob
import sys
import time

from app.core.dynamixel_interface import DynamixelInterface
from app.services.hand_control_controller import execute_gesture
from app.schemas.hand_profiles import ELEVEN_DOF_RIGHT, SIX_DOF_RIGHT, TWO_MOTORS
from app.utils.physics import (
    current_to_torque_nm,
    torque_to_fingertip_force,
    total_grip_force,
)
from app.utils.anthropometry import get_finger_length_m


def find_u2d2_port() -> str | None:

    env_port = os.getenv("DYNAMIXEL_PORT")
    if env_port and os.path.exists(env_port):
        return env_port

    # Linux estable por-id
    by_id = glob.glob("/dev/serial/by-id/*FTDI*")
    if by_id:
        # opcional: ordenar para elegir consistente
        by_id.sort()
        return by_id[0]

    # Linux fallback
    tty_usb = glob.glob("/dev/ttyUSB*")
    if tty_usb:
        tty_usb.sort()
        return tty_usb[0]

    # Windows fallback
    com_ports = glob.glob("COM[0-9]*")
    if com_ports:
        com_ports.sort()
        return com_ports[0]

    return None


def main() -> int:
    port = "COM16"
    if not port:
        print("[ERROR] - U2D2 no detectado. Conectar el dispositivo o define DYNAMIXEL_PORT.")
        return 1

    print(f"[INFO] - Usando puerto Dynamixel: {port}")

    dx = DynamixelInterface(port_name=port)

    try:
        dx.initialize()
        ids = dx.scan_motors()
    except Exception as e:
        print(f"[ERROR] - No se pudo inicializar/escanear Dynamixel en {port}: {e}")
        return 1

    if not ids:
        print("[ERROR] - No se detectaron motores. Revisar alimentación, baudrate, cableado, IDs.")
        return 1

    print("[TEST] - Ejecutando Gesto")
    """execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="BALL")"""


    print("[TEST] - Ejecutando secuencia REST → POINT")
	
    for i in range(1):
        print(f"\n[CICLO {i+1}] OPEN (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="ZERO")
        time.sleep(3.0)   # REST dura 5 segundos

        print(f"[CICLO {i+1}] REST (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="REST")
        time.sleep(3.0)   # POINT dura 4 segundos
        
        print(f"\n[CICLO {i+1}] CLOSE (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="CLOSE")
        time.sleep(3.0)   # REST dura 5 segundos

        print(f"[CICLO {i+1}] REST (4 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="REST")
        time.sleep(3.0)   # POINT dura 4 segundos

        print(f"\n[CICLO {i+1}] LIKE (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="LIKE")
        time.sleep(3.0)   # REST dura 5 segundos

        print(f"[CICLO {i+1}] REST (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="REST")
        time.sleep(3.0)   # POINT dura 4 segundos

        print(f"\n[CICLO {i+1}] POINT (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="POINT")
        time.sleep(3.0)   # REST dura 5 segundos

        print(f"[CICLO {i+1}] REST (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="REST")
        time.sleep(3.0)   # POINT dura 4 segundos
        
        print(f"\n[CICLO {i+1}] PINCH (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="PINCH")
        time.sleep(3.0)   # REST dura 5 segundos

        print(f"[CICLO {i+1}] REST (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="REST")
        time.sleep(3.0)   # POINT dura 4 segundos

        print(f"\n[CICLO {i+1}] CYLINDRICAL (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="CYLINDRICAL")
        time.sleep(3.0)   # REST dura 5 segundos

        print(f"[CICLO {i+1}] REST (4 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="REST")
        time.sleep(3.0)   # POINT dura 4 segundos

        print(f"\n[CICLO {i+1}] SPHERICAL (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="BALL")
        time.sleep(3.0)   # REST dura 5 segundos

        print(f"[CICLO {i+1}] REST (5 s)")
        execute_gesture(dx, ELEVEN_DOF_RIGHT, gesture_name="REST")
        time.sleep(3.0)   # POINT dura 4 segundos
    """try:
	execute_gesture(...)
        time.sleep(...)
    except KeyboardInterrupt:
	print("[INFO] Sesión cancelada por el usuario")
	break"""
        
    
    finger_forces: dict[str, float] = {}




    print("[TEST] - Calculando fuerzas por dedo")

    for finger_name, finger_profile in ELEVEN_DOF_RIGHT.fingers.items():
        # Tomar el primer motor NO bloqueado del dedo
        try:
            motor = next(m for m in finger_profile.motors.values() if not m.locked)
        except StopIteration:
            print(f"[WARN] - {finger_name}: no tiene motor libre (todos locked). Saltando.")
            continue

        # Si ese motor no existe en el bus, saltar sin romper todo
        if motor.motor_id not in ids:
            print(f"[WARN] - {finger_name}: motor ID {motor.motor_id} no está detectado. Saltando.")
            continue

        try:
            current_a = dx.read_current_amps(motor.motor_id)
        except Exception as e:
            print(f"[WARN] - {finger_name}: no se pudo leer corriente (ID {motor.motor_id}): {e}")
            continue

        torque_nm = current_to_torque_nm(current_a)
        lever_arm = get_finger_length_m(finger_name)
        force_n = torque_to_fingertip_force(torque_nm, lever_arm)

        finger_forces[finger_name] = force_n

        print(
            f"{finger_name}: "
            f"I={current_a:.3f} A | "
            f"T={torque_nm:.4f} Nm | "
            f"F={force_n:.2f} N"
        )

    total_force = total_grip_force(finger_forces)
    print(f"\n[RESULTADO] Fuerza total de agarre: {total_force:.2f} N")
    return 0


if __name__ == "__main__":
    sys.exit(main())
