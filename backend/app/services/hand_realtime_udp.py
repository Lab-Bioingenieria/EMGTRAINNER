import asyncio
import json
from typing import AsyncGenerator

async def udp_listener(port: int = 8765) -> AsyncGenerator[dict, None]:
    # Simple UDP listener that yields parsed JSON dicts
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    sock.setblocking(False)
    loop = asyncio.get_event_loop()
    while True:
        data, addr = await loop.run_in_executor(None, sock.recvfrom, 4096)
        try:
            obj = json.loads(data.decode('utf-8'))
            # debug log for received UDP test messages
            try:
                print(f"[hand_realtime_udp] recv from {addr}: {obj.get('gesture', '<no-gesture>')}")
            except Exception:
                pass
            yield obj
        except Exception:
            continue
