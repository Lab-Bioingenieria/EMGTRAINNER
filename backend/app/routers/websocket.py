from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import websocket_manager
from core.fastapi.dependencies.websocket_auth import authenticate_websocket

router = APIRouter()

@router.websocket("/ws/emg")
async def websocket_endpoint(websocket: WebSocket):
    if await authenticate_websocket(websocket) is None:
        return

    websocket_manager.register(websocket)
    try:
        while True:
            # Keep alive loop. We might receive commands here in the future.
            # For now just wait for messages (and ignore them) or handle disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)
