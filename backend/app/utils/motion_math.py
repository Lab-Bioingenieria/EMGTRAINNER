def clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(max_v, value))


def deg_to_ticks_xl330(deg: float) -> int:
    """
    XL330: 0–4095 ticks = 360°
    Centro = 2048
    """
    return int(2048 + (deg / 360.0) * 4096)


def ticks_to_deg_xl330(ticks: int) -> float:
    return ((ticks - 2048) / 4096.0) * 360.0
