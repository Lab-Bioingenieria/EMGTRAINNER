# anthropometry.py

SCALE_FACTOR = 1.85

FALANGES_MM = {
    "thumb":   [31.57,     0, 21.67],
    "index":   [39.78, 22.38, 15.82],
    "middle":  [44.63, 26.33, 17.40],
    "ring":    [41.37, 25.65, 17.30],
    "pinky":   [32.74, 18.11, 15.96],
}

def get_finger_length_m(finger: str) -> float:
    "Longitud total del dedo escalada"
    length_mm = sum(FALANGES_MM[finger]) * SCALE_FACTOR
    return length_mm / 1000.0
