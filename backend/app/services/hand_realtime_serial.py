import asyncio
import json
import time
from typing import AsyncGenerator

def open_serial(port: str, baud: int = 115200):
    try:
        import serial
        ser = serial.Serial(port, baud, timeout=0.1)
        return ser
    except Exception as e:
        print(f"[realtime.hand_realtime_serial] Could not open serial {port}: {e}")
        return None

async def serial_generator(port: str, baud: int = 115200) -> AsyncGenerator[dict, None]:
    ser = open_serial(port, baud)
    if ser is None:
        raise RuntimeError(f"Could not open serial port {port}")

    loop = asyncio.get_event_loop()
    while True:
        # read a line
        try:
            line = await loop.run_in_executor(None, ser.readline)
            if not line:
                await asyncio.sleep(0.01)
                continue
            try:
                s = line.decode('utf-8').strip()
            except Exception:
                s = str(line)
            # If line looks like CSV from ESP32, try parse and infer
            if ',' in s:
                try:
                    from app.services.serial_emg_reader import parse_line
                    from app.services.emg_inference_stub import infer_from_emg
                    parsed = parse_line(s)
                    if parsed:
                        gesture, conf = infer_from_emg(parsed.get('emg', []))
                        yield { 'ts': parsed.get('ts', time.time()), 'gesture': gesture, 'conf': conf, 'source': 'serial_emg' }
                        continue
                except Exception:
                    # fallthrough to try JSON
                    pass

            try:
                obj = json.loads(s)
                yield obj
            except Exception:
                # ignore unparsable
                continue
        except Exception:
            await asyncio.sleep(0.1)
