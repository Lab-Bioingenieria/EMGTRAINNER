"""Motor identification helpers.

Moving one motor at a time is the only reliable way to confirm that the
ID -> finger/joint mapping declared in a HandProfile matches the physical
wiring. The pure helpers live here so they can be tested without a bus.
"""
from typing import Optional, Tuple

from app.schemas.hand_profiles import HandProfile, MotorConfig

# Amplitude of the identification wiggle. Large enough to be unmistakable
# by eye, small enough to stay far from any mechanical stop.
WIGGLE_DEG = 35.0

# Fraction of the travel kept as a safety margin at each end, so the wiggle
# never drives a joint into its own limit.
EDGE_MARGIN = 0.15


def describe_motor(profile: HandProfile, motor_id: int) -> Optional[Tuple[str, str]]:
    """Return (finger_name, joint_name) for a motor id, or None if unmapped."""
    for finger_name, finger in profile.fingers.items():
        for joint_name, motor in finger.motors.items():
            if motor.motor_id == motor_id:
                return finger_name, joint_name
    return None


def wiggle_angles(motor: MotorConfig) -> Tuple[float, float]:
    """Two angles inside the motor's own limits, used as wiggle endpoints.

    A fixed amplitude would overshoot narrow joints such as the thumb
    CMC_FE (0-45 deg), so the span shrinks to fit whatever travel exists.
    A degenerate range collapses to a single angle instead of inverting.
    """
    span = motor.max_deg - motor.min_deg
    if span <= 0:
        return motor.min_deg, motor.min_deg

    margin = span * EDGE_MARGIN
    low = motor.min_deg + margin
    high = motor.max_deg - margin

    amplitude = min(WIGGLE_DEG, high - low)
    center = (low + high) / 2
    return center - amplitude / 2, center + amplitude / 2
