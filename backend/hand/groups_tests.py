from dynamixel_sdk import *
import time

PORT = "COM4"
BAUDRATE = 1000000
PROTOCOL = 2.0

ADDR_TORQUE = 64
ADDR_GOAL_CURRENT = 100

ADDR_GOAL_VELOCITY = 24
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_CURRENT = 126

TORQUE_ON = 1
TORQUE_OFF = 0

MAX_CURRENT = 140
LOW_SPEED = 25
COLLISION_CURRENT = 170

OPEN = 2000
CLOSE = 2500

groups = {
    "Pulgar": [1,2,3],
    "Indice": [4,5],
    "Medio": [6,7],
    "Anular": [8,9],
    "Menique": [10,11],
    "Muneca": [12,13]
}

port = PortHandler(PORT)
packet = PacketHandler(PROTOCOL)

port.openPort()
port.setBaudRate(BAUDRATE)

# Inicialización segura
for group in groups.values():
    for dxl in group:
        packet.write1ByteTxRx(port, dxl, ADDR_TORQUE, TORQUE_ON)
        packet.write2ByteTxRx(port, dxl, ADDR_GOAL_CURRENT, MAX_CURRENT)
        packet.write4ByteTxRx(port, dxl, ADDR_GOAL_VELOCITY, LOW_SPEED)

def collision(group):
    for dxl in group:
        current,_,_ = packet.read2ByteTxRx(port, dxl, ADDR_PRESENT_CURRENT)
        if current > COLLISION_CURRENT:
            print(f"⚠ Colisión en motor {dxl} → {current}")
            return True
    return False

def move_group(group, pos):
    groupSync = GroupSyncWrite(port, packet, ADDR_GOAL_POSITION, 4)
    for dxl in group:
        p = [pos & 0xFF,(pos>>8)&0xFF,(pos>>16)&0xFF,(pos>>24)&0xFF]
        groupSync.addParam(dxl,p)
    groupSync.txPacket()

# --- PRUEBA ---
try:
    for name, motors in groups.items():
        print(f"\nProbando grupo: {name}")

        print("Abriendo")
        move_group(motors, OPEN)
        for _ in range(50):
            if collision(motors):
                break
            time.sleep(0.05)

        time.sleep(1)

        print("Cerrando")
        move_group(motors, CLOSE)
        for _ in range(50):
            if collision(motors):
                break
            time.sleep(0.05)

        input("Presiona ENTER para continuar al siguiente grupo...")

except KeyboardInterrupt:
    pass

# Apagar torque
for group in groups.values():
    for dxl in group:
        packet.write1ByteTxRx(port, dxl, ADDR_TORQUE, TORQUE_OFF)

port.closePort()
