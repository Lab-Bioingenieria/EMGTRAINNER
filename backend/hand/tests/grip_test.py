from core.dynamixel_interface import DynamixelInterface
from control.hand_controller import move_hand_profile
from models.hand_profiles import SIX_DOF_HAND
from core.physics import (current_to_torque_nm, torque_to_fingertip_force, total_grip_force,)
from models.anthropometry import get_finger_length_m

def main():
    dx = DynamixelInterface(port_name="COM4")
    dx.initialize()
    dx.scan_motors()

    print("[TEST] - Ejecutando gesto SALUDAR")
    move_hand_profile(dx, SIX_DOF_HAND, gesture_name="SALUTE")

    finger_forces = {}

    print("[TEST] - Calculando fuerzas por dedo")

    for finger_name, finger_profile in SIX_DOF_HAND.fingers.items():

        # Usar el primer motor libre del dedo
        motor = next(
            m for m in finger_profile.motors.values() if not m.locked
        )

        current_a = dx.read_current_amps(motor.motor_id)
        torque_nm = current_to_torque_nm(current_a)

        lever_arm = get_finger_length_m(finger_name)
        force_n = torque_to_fingertip_force(torque_nm, lever_arm)

        finger_forces[finger_name] = force_n

        print(
            f"{finger_name}: "
            f"I={current_a:.3f} A | "
            f"T={torque_nm:.4f} Nm | "
            f"F={force_n:.2f} N"
        )

    total_force = total_grip_force(finger_forces)
    print(f"\n[RESULTADO] Fuerza total de agarre: {total_force:.2f} N")


if __name__ == "__main__":
    main()
