import asyncio
import os
import time
import json
from typing import Set
from fastapi import WebSocket

from .models import GestureEvent
from .planner import GesturePlanner

from .sources import mock_source, serial_source, udp_source


class RealtimeManager:
    def __init__(self):
        self.clients: Set[WebSocket] = set()
        self.planner = GesturePlanner(
            min_conf=float(os.getenv('MIN_CONF', 0.6)),
            cooldown_s=float(os.getenv('COOLDOWN_S', 0.15)),
            respect_play=bool(int(os.getenv('RESPECT_PLAY', '1'))),
        )
        self.source = os.getenv('JOINT_SOURCE', 'mock')
        self.udp_port = int(os.getenv('UDP_PORT', 8765))
        self.emg_port = os.getenv('EMG_PORT', None)
        self.update_hz = float(os.getenv('UPDATE_HZ', 30))

        self._task = None
        self._running = False

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    async def register(self, ws: WebSocket):
        self.clients.add(ws)
        # ensure source running
        await self.start()

    async def unregister(self, ws: WebSocket):
        try:
            self.clients.remove(ws)
        except KeyError:
            pass

    async def broadcast(self, payload: dict):
        to_remove = []
        for ws in list(self.clients):
            try:
                await ws.send_json(payload)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            await self.unregister(ws)

    async def _run(self):
        # pick source
        print(f"[realtime.manager] starting source {self.source}")
        try:
            if self.source == 'serial' and self.emg_port:
                try:
                    agen = serial_source.serial_generator(self.emg_port)
                except Exception as e:
                    print(f"[realtime.manager] serial source failed opening: {e}. Falling back to mock.")
                    agen = mock_source.mock_generator(rate_hz=1.0)
            elif self.source == 'udp':
                agen = udp_source.udp_listener(self.udp_port)
            else:
                agen = mock_source.mock_generator(rate_hz=1.0)

            async for item in agen:
                # item may be dict or GestureEvent
                if isinstance(item, dict):
                    try:
                        ev = GestureEvent(**item)
                    except Exception:
                        # try to map keys
                        ev = GestureEvent(ts=time.time(), gesture=item.get('gesture','UNKNOWN'), conf=float(item.get('conf',0.0)), source=item.get('source'))
                else:
                    ev = item

                planned = self.planner.accept(ev)
                if planned:
                    payload = {
                        'ts': time.time(),
                        'gesture': planned.gesture,
                        'play_mode': planned.play_mode,
                        'intermediate': planned.intermediate or [],
                    }
                    await self.broadcast(payload)
                await asyncio.sleep(1.0 / max(1.0, self.update_hz))
        except asyncio.CancelledError:
            print('[realtime.manager] cancelled')
        except Exception as e:
            print(f'[realtime.manager] error: {e}')
        finally:
            self._running = False


manager = RealtimeManager()
