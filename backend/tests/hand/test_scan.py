import os
import glob
from app.core.dynamixel_interface import DynamixelInterface, find_u2d2_port

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
