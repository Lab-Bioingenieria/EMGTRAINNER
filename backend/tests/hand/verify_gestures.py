"""Execute gestures and prove the hand actually reached them.

grip_test prints gesture names and returns 0 even if nothing moves. This
runs the same gestures through the same production path, then reads every
commanded motor back and reports the error per finger.

    python -m tests.hand.verify_gestures            # default gesture set
    python -m tests.hand.verify_gestures CLOSE POINT
"""
import sys
import time

from app.core.dynamixel_interface import DynamixelInterface, find_u2d2_port
from app.schemas.hand_gestures import GESTURES
from app.schemas.hand_profiles import ELEVEN_DOF_RIGHT
from app.services.hand_control_controller import (
    execute_gesture,
    _collect_targets_for_fingers,
)
from app.services.hand_identify import describe_motor

PROFILE = ELEVEN_DOF_RIGHT
DEFAULT_GESTURES = ["ZERO", "CLOSE", "POINT", "PINCH", "LIKE", "CYLINDRICAL", "BALL", "REST"]

# Healthy joints land within a few ticks; motor 3 sits ~70 ticks short of a
# target it cannot physically reach. 30 ticks is ~2.6 deg.
ARRIVAL_TOLERANCE_TICKS = 30
SETTLE_S = 1.2


def main() -> int:
    names = [a.upper() for a in sys.argv[1:]] or DEFAULT_GESTURES

    port = find_u2d2_port()
    if not port:
        print("[ERROR] - U2D2 no detectado.")
        return 1

    dx = DynamixelInterface(port_name=port)
    dx.initialize()
    present = dx.scan_motors()
    print(f"\n[INFO] - {len(present)} motores en el bus: {present}")

    failures = 0
    for name in names:
        if name not in GESTURES or PROFILE.name not in GESTURES[name]:
            print(f"\n[SKIP] {name}: no definido para {PROFILE.name}")
            continue

        gesture = GESTURES[name][PROFILE.name]
        targets, _ = _collect_targets_for_fingers(dx, PROFILE, gesture, list(gesture.keys()))

        execute_gesture(dx, PROFILE, gesture_name=name)
        time.sleep(SETTLE_S)

        print(f"\n===== {name} =====")
        print(f"  {'motor':>5} {'dedo/articulacion':<18} {'objetivo':>9} {'real':>7} {'error':>6}  estado")
        arrived = 0
        for motor_id, goal in sorted(targets.items()):
            actual = dx.read_position(motor_id)
            error = abs(actual - goal)
            ok = error <= ARRIVAL_TOLERANCE_TICKS
            arrived += ok
            finger, joint = describe_motor(PROFILE, motor_id) or ("?", "?")
            print(f"  {motor_id:>5} {finger + '/' + joint:<18} {goal:>9} {actual:>7} {error:>6}"
                  f"  {'OK' if ok else 'NO LLEGO'}")

        total = len(targets)
        status = "OK" if arrived == total else "INCOMPLETO"
        print(f"  -> {arrived}/{total} motores en posicion  [{status}]")
        if arrived != total:
            failures += 1

    for motor_id in present:
        dx.disable_torque(motor_id)
    print(f"\n[FIN] torque liberado. Gestos incompletos: {failures}/{len(names)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
