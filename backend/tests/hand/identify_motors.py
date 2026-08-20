"""Move motors one at a time so a human can confirm the ID -> finger map.

Each motor wiggles alone, inside its own profile limits, and torque is
released before moving on. Usage:

    python -m tests.hand.identify_motors            # every mapped motor
    python -m tests.hand.identify_motors 1 2 3      # only these ids
"""
import sys
import time

from app.core.dynamixel_interface import DynamixelInterface, find_u2d2_port
from app.schemas.hand_profiles import ELEVEN_DOF_RIGHT
from app.services.hand_identify import describe_motor, wiggle_angles

PROFILE = ELEVEN_DOF_RIGHT
HOLD_S = 1.2


def _motor_by_id(motor_id: int):
    for finger in PROFILE.fingers.values():
        for motor in finger.motors.values():
            if motor.motor_id == motor_id:
                return motor
    return None


def main() -> int:
    requested = [int(a) for a in sys.argv[1:]]

    port = find_u2d2_port()
    if not port:
        print("[ERROR] - U2D2 no detectado. Conecta el dispositivo o define DYNAMIXEL_PORT.")
        return 1

    dx = DynamixelInterface(port_name=port)
    dx.initialize()
    present = dx.scan_motors()

    ids = requested or [
        m.motor_id for f in PROFILE.fingers.values() for m in f.motors.values()
    ]

    for motor_id in ids:
        motor = _motor_by_id(motor_id)
        claim = describe_motor(PROFILE, motor_id)

        if motor is None or claim is None:
            print(f"\n[SKIP] ID {motor_id}: no está en el perfil {PROFILE.name}")
            continue
        if motor_id not in present:
            print(f"\n[SKIP] ID {motor_id}: no respondió al ping")
            continue

        finger, joint = claim
        low, high = wiggle_angles(motor)
        print(f"\n===== ID {motor_id} =====")
        print(f"  el perfil dice : {finger} / {joint}")
        print(f"  limites        : {motor.min_deg:.0f}-{motor.max_deg:.0f} deg")
        print(f"  moviendo entre : {low:.1f} y {high:.1f} deg  <-- MIRA LA MANO")

        start = dx.read_position(motor_id)
        try:
            # Sample at every waypoint: a start-vs-end delta cannot tell a
            # completed round trip apart from a motor that never moved.
            reached = []
            for angle in (low, high, low):
                goal = dx.degrees_to_ticks_centered(angle)
                dx.move_motor_safe(motor_id, goal, timeout_s=HOLD_S)
                reached.append((goal, dx.read_position(motor_id)))

            print(f"  posicion inicial: {start} ticks")
            for step, (goal, actual) in enumerate(reached, start=1):
                print(f"  paso {step}: objetivo {goal:>5} -> real {actual:>5} (error {abs(actual - goal):>4})")

            excursion = max(a for _, a in reached) - min(a for _, a in reached)
            verdict = "SE MOVIO" if excursion > 50 else "NO SE MOVIO"
            print(f"  excursion real : {excursion} ticks  -> {verdict}")
        except Exception as exc:
            print(f"  [ERROR] {exc}")
        finally:
            dx.disable_torque(motor_id)

        time.sleep(0.6)

    print("\n[FIN] torque liberado en los motores probados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
