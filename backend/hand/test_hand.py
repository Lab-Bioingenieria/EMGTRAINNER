from dynamixel_sdk import *
import time

# -------------------- CONFIGURACIÓN --------------------

PORT = "/dev/ttyUSB0"   # Linux (Jetson)
# PORT = "COM17"       # Windows

BAUDRATE = 57600
PROTOCOL = 2.0

DXL_IDS = list(range(1,14))   # 13 motores

ADDR_TORQUE_ENABLE   = 64
ADDR_GOAL_CURRENT    = 102
ADDR_GOAL_VELOCITY   = 104
ADDR_GOAL_POSITION   = 116
ADDR_PRESENT_CURRENT= 126
ADDR_PRESENT_POSITION = 132

TORQUE_ON = 1
TORQUE_OFF = 0

MAX_CURRENT = 150
LOW_SPEED = 30

OPEN_POS = 2600
CLOSE_POS = 1500

COLLISION_CURRENT = 180   # Si supera esto → detener

# -------------------- INICIALIZACIÓN --------------------

port = PortHandler(PORT)
packet = PacketHandler(PROTOCOL)

if not port.openPort():
    raise RuntimeError("No se pudo abrir el puerto")

if not port.setBaudRate(BAUDRATE):
    raise RuntimeError("No se pudo configurar baudrate")

# -------------------- HABILITAR MOTORES --------------------

for dxl in DXL_IDS:
    packet.write1ByteTxRx(port, dxl, ADDR_TORQUE_ENABLE, TORQUE_ON)
    packet.write2ByteTxRx(port, dxl, ADDR_GOAL_CURRENT, MAX_CURRENT)
    packet.write4ByteTxRx(port, dxl, ADDR_GOAL_VELOCITY, LOW_SPEED)

print("Motores listos con límites seguros")

# -------------------- FUNCIÓN DE MOVIMIENTO --------------------

def move_all(position):
    group = GroupSyncWrite(port, packet, ADDR_GOAL_POSITION, 4)

    for dxl in DXL_IDS:
        param = [
            position & 0xFF,
            (position >> 8) & 0xFF,
            (position >> 16) & 0xFF,
            (position >> 24) & 0xFF
        ]
        group.addParam(dxl, param)

    group.txPacket()

# -------------------- MONITOREO DE COLISIONES --------------------

def collision_detected():
    for dxl in DXL_IDS:
        current, _, _ = packet.read2ByteTxRx(port, dxl, ADDR_PRESENT_CURRENT)
        if current > COLLISION_CURRENT:
            print(f"⚠ COLISIÓN detectada en motor {dxl}  Corriente = {current}")
            return True
    return False

# -------------------- PRUEBA --------------------

try:
    while True:
        print("Abriendo mano")
        move_all(OPEN_POS)
        for _ in range(50):
            if collision_detected():
                break
            time.sleep(0.05)

        print("Cerrando mano")
        move_all(CLOSE_POS)
        for _ in range(50):
            if collision_detected():
                break
            time.sleep(0.05)

except KeyboardInterrupt:
    print("Parada manual")

# -------------------- APAGAR TODO --------------------

for dxl in DXL_IDS:
    packet.write1ByteTxRx(port, dxl, ADDR_TORQUE_ENABLE, TORQUE_OFF)

port.closePort()
