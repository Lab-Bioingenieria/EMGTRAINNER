import os
import glob
from hand.core.dynamixel_interface import DynamixelInterface


def find_u2d2_port():
    # 1) Si el env está y existe
    env_port = os.getenv("DYNAMIXEL_PORT")
    if env_port and os.path.exists(env_port):
        return env_port

    # 2) Buscar por-id (estable)
    candidates = glob.glob("/dev/serial/by-id/*FTDI*")
    if candidates:
        return candidates[0]

    # 3) Fallback: ttyUSB*
    usb = glob.glob("/dev/ttyUSB*")
    if usb:
        return usb[0]

    return None


def main():
    port = find_u2d2_port()
    if not port:
        print("U2D2 no detectado. Conecta el dispositivo.")
        return 1

    print("Usando puerto:", port)

    dx = DynamixelInterface(port)
    dx.initialize()
    ids = dx.scan_motors()
    print("Motores detectados:", ids)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
