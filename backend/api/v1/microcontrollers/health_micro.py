from fastapi import APIRouter, Depends

from serial.tools import list_ports
from app.core.hardware_config import hardware_config
from app.schemas.hardware import HardwareConfigResponse, HardwareConfigUpdate
from core.fastapi.dependencies.authentication import AuthenticationRequired

health_microcontroller_router = APIRouter(
    dependencies=[Depends(AuthenticationRequired)]
)

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
        data_port=config.data_port,
        sensor_type=config.sensor_type,
        motor_type=config.motor_type
    )
    # The hand may be holding the previous port (or a dead handle from a
    # replugged adapter). Drop it so the next gesture reconnects using the
    # configuration just saved. Imported lazily: emg_service pulls in the
    # serial/websocket stack, which this router does not otherwise need.
    from app.services.emg_service import emg_service
    from app.services.hand_service import HandService

    emg_service.disconnect_hand()
    HandService.get_instance().release_hardware()
    return hardware_config.get_config()