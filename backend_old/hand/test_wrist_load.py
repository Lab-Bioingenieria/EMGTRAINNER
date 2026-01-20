from dynamixel_sdk import *
import time

PORT = "COM4"
BAUDRATE = 57600
PROTOCOL = 2.0

WRIST = [12, 13]

ADDR_TORQUE = 64
ADDR_GOAL_CURRENT = 102
ADDR_GOAL_VELOCITY = 104
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_CURRENT = 126
ADDR_PRESENT_POSITION = 132

TORQUE_ON = 1

MAX_CURRENT = 300    # permitimos torque alto solo para prueba
LOW_SPEED = 20

port = PortHandler(PORT)
packet = PacketHandler(PROTOCOL)

port.openPort()
port.setBaudRate(BAUDRATE)

# Configurar motores
for dxl in WRIST:
    packet.write1ByteTxRx(port, dxl, ADDR_TORQUE, TORQUE_ON)
    packet.write2ByteTxRx(port, dxl, ADDR_GOAL_CURRENT, MAX_CURRENT)
    packet.write4ByteTxRx(port, dxl, ADDR_GOAL_VELOCITY, LOW_SPEED)

# Leer posición actual
pos = {}
for dxl in WRIST:
    p,_,_ = packet.read4ByteTxRx(port, dxl, ADDR_PRESENT_POSITION)
    pos[dxl] = p

# Fijar posición actual
for dxl in WRIST:
    packet.write4ByteTxRx(port, dxl, ADDR_GOAL_POSITION, pos[dxl])

print("Muñeca fijada. Midiendo carga estática...")

samples = {12: [], 13: []}

for i in range(200):   # 10 segundos
    for dxl in WRIST:
        cur,_,_ = packet.read2ByteTxRx(port, dxl, ADDR_PRESENT_CURRENT)
        samples[dxl].append(cur)
    time.sleep(0.05)

# Resultados
for dxl in WRIST:
    avg = sum(samples[dxl]) / len(samples[dxl])
    peak = max(samples[dxl])
    print(f"Motor {dxl}: Corriente promedio = {avg:.1f}  Pico = {peak}")

port.closePort()
