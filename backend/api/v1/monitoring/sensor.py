from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.services import emg_service
from app.services.websocket_manager import websocket_manager
from core.fastapi.dependencies.authentication import AuthenticationRequired
from core.fastapi.dependencies.websocket_auth import authenticate_websocket

sensor_router = APIRouter(dependencies=[Depends(AuthenticationRequired)])
# WebSocket routes cannot use HTTP dependencies; they authenticate explicitly.
sensor_ws_router = APIRouter()

@sensor_ws_router.websocket("/ws/emg-stream")
async def websocket_emg_stream(websocket: WebSocket):
    """Live EMG feed for the browser plotter.

    This endpoint is a pure *subscriber*. The acquisition thread in
    ``EMGDataService._streaming_loop`` is the only reader of the serial port and
    publishes every sample through ``websocket_manager``. Reading the port here
    as well split the byte stream between two consumers (garbled uMyo frames,
    duplicated CSV rows) and tied the recording session to whether a chart
    happened to be open. Starting and stopping a session stays with the REST
    endpoints ``/emg/start`` and ``/emg/stop``.
    """
    if await authenticate_websocket(websocket) is None:
        return

    websocket_manager.register(websocket)
    try:
        # Keep-alive: incoming messages are ignored, we only need to notice
        # the client going away.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(websocket)


@sensor_router.get("/emg/status")
async def get_emg_status():
    """Get current EMG sensor connection status"""
    return emg_service.get_connection_status()


@sensor_router.post("/emg/connect")
async def connect_emg(port: str = None):
    """Manually connect to ESP32 on specific port"""
    return emg_service.connect_to_device(port)


@sensor_router.post("/emg/disconnect")
async def disconnect_emg():
    """Disconnect from ESP32"""
    return emg_service.disconnect_from_device()


@sensor_router.post("/emg/start")
async def start_emg_session(category: str = ""):
    """Send START_SESSION command to ESP32"""
    # Esto solo prende la adquisicion/transmision de datos del sensor: no
    # mueve la mano Dynamixel (eso pasa por /hand/session/start, que si
    # exige el reset del e-stop). Por eso no depende del interlock de
    # movimiento: si dependiera, habria que resetear el e-stop cada vez
    # que se reinicia el backend solo para poder grabar EMG.

    # Ensure we are connected first
    status = emg_service.get_connection_status()
    if not status["connected"]:
        return {"error": "Device not connected. Connect first."}
        
    emg_service.start_streaming(category=category)
    return {"message": "Session started", "status": "streaming", "category": category}


@sensor_router.post("/emg/stop")
async def stop_emg_session():
    """Send STOP_SESSION command to ESP32"""
    emg_service.stop_streaming()
    return {"message": "Session stopped", "status": "idle"}


@sensor_router.post("/emg/session/info")
async def set_session_info(name: str, age: str = None):
    """Set patient name for current/next session"""
    emg_service.set_session_info(name, age)
    return {"message": f"Session info updated: {name} ({age})"}


@sensor_router.post("/emg/label")
async def set_movement_label(label: str):
    """Set current movement label"""
    emg_service.set_current_label(label)
    return {"message": f"Label updated: {label}"}


@sensor_router.get("/emg/sample")
async def get_emg_sample():
    """Get a single sample of EMG data (for testing)"""
    data = emg_service.read_emg_sample()
    if data:
        return data
    
    return {
        "error": "No valid data received or not connected",
        "connected": emg_service.get_connection_status()["connected"]
    }
