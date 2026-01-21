from core.dynamixel_interface import DynamixelInterface

def main():
    dx = DynamixelInterface(port_name="COM4")  # usa el COM correcto
    dx.initialize()
    ids = dx.scan_motors()
    print("Motores detectados:", ids)

if __name__ == "__main__":
    main()
