from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

from app.services import emg_service

sensor_router = APIRouter()

# Store active WebSocket connections
active_connections: List[WebSocket] = []


@sensor_router.websocket("/ws/emg-stream")
async def websocket_emg_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time EMG data streaming"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Connect to ESP32 if not already connected
        status = emg_service.get_connection_status()
        if not status["connected"]:
            result = emg_service.connect_to_device()
            if not result["success"]:
                await websocket.send_json({
                    "error": "Could not connect to ESP32"
                })
                # We don't return here to keep connection open for retries or status updates
                # but in strict logic, maybe we should close? Leaving open as per apparent original intent.
        
        # Start streaming data
        emg_service.start_streaming()
        
        while True:
            # We access the serial manager directly for the stream loop to avoid overhead
            # or add a specific method in service for 'next line'.
            # Using service method read_line would be cleaner if exposed, 
            # but we can use the manager via service for now or add a helper in service.
            
            # Let's assume we want to use the service's logic.
            # We need a non-blocking way or small timeout read.
            # The service's serial_manager.read_line() is synchronous.
            
            # To avoid blocking the event loop too much, we sleep.
            # Ideally serial reading should be threaded, but for MVP this is okay.
            
            line = emg_service.serial_manager.read_line()
            
            if line:
                data = emg_service.parse_emg_line(line)
                if data:
                    await websocket.send_json(data)
            
            await asyncio.sleep(0.001)  # Context switch
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        if len(active_connections) == 0:
            emg_service.stop_streaming()
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            active_connections.remove(websocket)
        except ValueError:
            pass
        if len(active_connections) == 0:
            emg_service.stop_streaming()


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
async def set_session_info(name: str):
    """Set patient name for current/next session"""
    emg_service.set_session_info(name)
    return {"message": f"Session info updated: {name}"}


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
