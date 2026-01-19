import time
from dynamixel_interface import DynamixelInterface
from hand_profiles import HandProfile

def move_hand_profile(dx: DynamixelInterface, profile: HandProfile, close: bool = True, delay_between_groups: float = 0.3,):
    for finger_name in profile.sequence:
        finger = profile.fingers[finger_name]
        print(f"[HAND] - Moviendo Grupo: {finger_name}")

        for motor_id in finger.motor_ids:
            target_deg = finger.close_deg if close else finger.open_deg
            target_ticks = dx.degrees_to_ticks_centered(target_deg)

            dx.set_profile_velocity(motor_id, finger.velocity)
            dx.set_current_limit(
                motor_id,
                dx.amps_to_current_units(finger.max_current_a)
            )

            dx.move_motor_safe(motor_id, target_ticks)

        time.sleep(delay_between_groups)
