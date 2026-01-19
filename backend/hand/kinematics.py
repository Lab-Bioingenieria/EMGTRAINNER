# backend/hand/kinematics.py

FALANGES_MM = {
    "thumb":  [58.41, 0.0, 40.09],
    "index":  [73.59, 41.40, 29.27],
    "middle": [82.56, 48.72, 32.19],
    "ring":   [76.53, 47.45, 32.01],
    "pinky":  [60.57, 33.50, 29.53],
}

def falange_lengths_m(finger: str):
    """Devuelve longitudes de falanges en metros"""
    return [l / 1000.0 for l in FALANGES_MM[finger]]
