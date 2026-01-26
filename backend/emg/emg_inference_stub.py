"""Simple EMG inference stub: maps 3-channel EMG samples to gesture labels.
This is a placeholder until the real model runs on Jetson and outputs gestures.
"""
import random
from typing import Tuple

GESTURES = ['OPEN','CLOSE','POINT','LIKE','CYLINDRICAL','SPHERICAL','SALUTE','PINCH','REST','ZERO']

def infer_from_emg(sample: list[float]) -> Tuple[str, float]:
    # naive rule: compare sums / thresholds
    if not sample or len(sample) < 3:
        return 'REST', 0.2
    s = sum(abs(x) for x in sample)
    # thresholds tuned arbitrarily for stub
    if s < 10:
        return 'REST', 0.6
    if sample[0] > 150:
        return 'POINT', 0.85
    if sample[1] > 150:
        return 'PINCH', 0.88
    if sample[2] > 160:
        return 'CLOSE', 0.9
    # random minor gestures
    return random.choice(GESTURES), 0.5
