from fastapi import APIRouter

from serial.tools import list_ports
from app.core.hardware_config import hardware_config
from app.schemas.hardware import HardwareConfigResponse, HardwareConfigUpdate

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

@health_microcontroller_router.get("/config", response_model=HardwareConfigResponse)
def get_config():
    """Get the current hardware configuration."""
    return hardware_config.get_config()

@health_microcontroller_router.post("/config", response_model=HardwareConfigResponse)
def update_config(config: HardwareConfigUpdate):
    """Update the hardware configuration."""
    hardware_config.save_config(
        main_port=config.main_port,
        independent_data_acquisition=config.independent_data_acquisition,
        data_port=config.data_port
    )
    return hardware_config.get_config()