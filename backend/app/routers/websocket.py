from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import websocket_manager

router = APIRouter()

@router.websocket("/ws/emg")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
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
