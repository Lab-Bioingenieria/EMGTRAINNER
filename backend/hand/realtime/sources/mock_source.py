import asyncio
import time
from ..models import GestureEvent

async def mock_generator(rate_hz: float = 1.0):
    gestures = ['OPEN','CLOSE','PINCH','POINT','LIKE','CYLINDRICAL','SPHERICAL','SALUTE','REST','ZERO']
    idx = 0
    interval = 1.0 / max(0.1, rate_hz)
    while True:
        gs = gestures[idx % len(gestures)]
        ev = GestureEvent(ts=time.time(), gesture=gs, conf=0.9, source='mock')
        yield ev
        idx += 1
        await asyncio.sleep(interval)
