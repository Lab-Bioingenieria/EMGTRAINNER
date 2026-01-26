from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from hand.realtime.manager import manager

router = APIRouter()


@router.websocket('/ws/gesture')
async def websocket_gesture(ws: WebSocket):
    await ws.accept()
    await manager.register(ws)
    try:
        while True:
            # Keep connection alive; server pushes events
            data = await ws.receive_text()
            # echo or handle basic control messages
            if data == 'ping':
                await ws.send_text('pong')
    except WebSocketDisconnect:
        await manager.unregister(ws)
    except Exception:
        await manager.unregister(ws)


@router.websocket('/ws/joint-state')
async def websocket_joint(ws: WebSocket):
    # For now, reuse gesture websocket (could be extended to emit JointState)
    await websocket_gesture(ws)
