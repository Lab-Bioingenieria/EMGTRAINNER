"""Serial EMG CSV parser.
Expected line format (CSV):
timestamp,session_time,emg1,emg2,emg3,movement_id,movement_name

This module exposes `parse_line` which returns a dict with parsed values.
"""
from typing import Optional, Dict

def parse_line(line: str) -> Optional[Dict]:
    try:
        s = line.strip()
        if not s:
            return None
        parts = s.split(',')
        if len(parts) < 7:
            return None
        ts = float(parts[0])
        session_time = float(parts[1])
        emg1 = float(parts[2])
        emg2 = float(parts[3])
        emg3 = float(parts[4])
        movement_id = parts[5]
        movement_name = parts[6]
        return {
            'ts': ts,
            'session_time': session_time,
            'emg': [emg1, emg2, emg3],
            'movement_id': movement_id,
            'movement_name': movement_name
        }
    except Exception:
        return None
