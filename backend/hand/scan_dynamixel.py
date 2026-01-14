from dynamixel_sdk import *

# ---------------- CONFIG ----------------

#PORT = "/dev/ttyUSB0"   # Jetson
PORT = "COM4"       # Windows

BAUDRATE = 1000000
PROTOCOL = 2.0

ADDR_MODEL_NUMBER = 0
ADDR_FIRMWARE_VERSION = 6

# ---------------- INICIALIZAR ----------------

port = PortHandler(PORT)
packet = PacketHandler(PROTOCOL)

if not port.openPort():
    raise RuntimeError("No se pudo abrir el puerto")

if not port.setBaudRate(BAUDRATE):
    raise RuntimeError("No se pudo configurar baudrate")

print("Escaneando bus DYNAMIXEL...")

found = []

# ---------------- ESCANEO ----------------

for dxl_id in range(0, 253):
    model, comm, err = packet.read2ByteTxRx(port, dxl_id, ADDR_MODEL_NUMBER)
    
    if comm == COMM_SUCCESS:
        firmware, _, _ = packet.read1ByteTxRx(port, dxl_id, ADDR_FIRMWARE_VERSION)
        print(f"ID {dxl_id:3d}  | Modelo {model}  | Firmware {firmware}")
        found.append(dxl_id)

# ---------------- RESULTADO ----------------

print("\nMotores detectados:", found)

port.closePort()
