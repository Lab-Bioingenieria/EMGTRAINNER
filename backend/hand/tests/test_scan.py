import  os
from hand.core.dynamixel_interface import DynamixelInterface

def main():
    port = os.getenv(
            "DYNAMIXEL_PORT",
            "/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTAO520W-if00-port0"
        )

    dx = DynamixelInterface(port)
    dx.initialize()
    ids = dx.scan_motors()
    print("Motores detectados:", ids)

if __name__ == "__main__":
    main()
