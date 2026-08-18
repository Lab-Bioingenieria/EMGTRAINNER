"""Read-only Dynamixel bus inventory.

Reports the configured/discovered port, Protocol 2.0, baudrate, and each
responding motor ID with its raw model number. Never enables torque or
writes any register — safe to run before any motion test.

Usage (from backend/, with the venv active):
    python -m tests.hand.inventory_scan
"""
import sys

from app.core.dynamixel_interface import DynamixelInterface, find_u2d2_port, inventory_report


def main() -> int:
    port = find_u2d2_port()
    if not port:
        print("[ERROR] - U2D2 no detectado. Conecta el dispositivo o define DYNAMIXEL_PORT.")
        return 1

    dx = DynamixelInterface(port_name=port)

    try:
        dx.initialize()
        report = inventory_report(dx)
    except Exception as e:
        print(f"[ERROR] - No se pudo inicializar/inventariar el bus en {port}: {e}")
        return 1

    print(f"[INFO] - Puerto:      {report['port']}")
    print(f"[INFO] - Protocolo:   {report['protocol_version']}")
    print(f"[INFO] - Baudrate:    {report['baudrate']}")

    if not report["motors"]:
        print("[WARN] - No se detectaron motores. Revisar alimentación, cableado, IDs.")
        return 1

    for motor in report["motors"]:
        print(
            f"[OK]   - ID {motor['id']:>2} -> "
            f"model_number={motor['model_number']} model_name={motor['model_name']}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
