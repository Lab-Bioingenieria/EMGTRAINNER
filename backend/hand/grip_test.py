from hand.dynamixel_interface import DynamixelInterface
from hand.hand_profiles import SIX_DOF_HAND
from hand.group_motion import move_hand_profile

dx = DynamixelInterface()
dx.initialize()
dx.scan_motors()

print("[TEST] Ejecutando cierre de mano")
move_hand_profile(dx, SIX_DOF_HAND, close=True)
