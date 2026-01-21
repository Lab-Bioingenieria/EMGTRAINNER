from fastapi import APIRouter

from serial.tools import list_ports

health_microcontroller_router = APIRouter()

@health_microcontroller_router.get("/ports")
def ports():
    ports = []

    for p in list_ports.comports():
        ports.append({
            "port": p.device,
            "description": p.description,
            "hwid": p.hwid
        })

    return {
        "count": len(ports),
        "ports": ports
    }