from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time

from hand.realtime.manager import manager

router = APIRouter()


class DevJointState(BaseModel):
    ts: float | None = None
    gesture: str | None = None
    conf: float | None = None
    mode: str | None = None
    joints: dict | None = None


@router.post('/dev/joint-state')
async def emit_joint_state(js: DevJointState):
    payload = {
        'ts': js.ts or time.time(),
        'gesture': js.gesture or 'UNKNOWN',
        'conf': js.conf or 0.0,
        'mode': js.mode or 'NLA',
        'joints': js.joints or {}
    }
    try:
        # ensure manager running
        await manager.start()
        await manager.broadcast(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'status': 'ok'}
