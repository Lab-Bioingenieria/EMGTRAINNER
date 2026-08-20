from app.schemas.hand_profiles import ELEVEN_DOF_RIGHT, SIX_DOF_RIGHT, MotorConfig
from app.services.hand_identify import describe_motor, wiggle_angles


def test_describe_motor_resolves_finger_and_joint_from_profile():
    assert describe_motor(ELEVEN_DOF_RIGHT, 1) == ("thumb", "MCP_FE")
    assert describe_motor(ELEVEN_DOF_RIGHT, 2) == ("thumb", "CMC_AA")


def test_describe_motor_returns_none_for_unmapped_id():
    assert describe_motor(ELEVEN_DOF_RIGHT, 99) is None


def test_wiggle_angles_stay_inside_the_motor_limits():
    motor = MotorConfig(4, 0, 90, 0, 0.8)
    low, high = wiggle_angles(motor)

    assert motor.min_deg <= low < high <= motor.max_deg


def test_wiggle_angles_shrink_to_fit_a_narrow_range():
    """The thumb CMC_FE only spans 45 deg; a fixed amplitude would overshoot."""
    motor = MotorConfig(3, 0, 45, 0, 0.8)
    low, high = wiggle_angles(motor)

    assert motor.min_deg <= low < high <= motor.max_deg


def test_wiggle_angles_never_invert_on_a_degenerate_range():
    motor = MotorConfig(12, 30, 30, 30, 0.8)
    low, high = wiggle_angles(motor)

    assert low == high == 30


# Physical identification on the assembled right hand showed the daisy chain
# runs from the pinky inward: 4/5 pinky, 6/7 ring, 8/9 middle, 10/11 index.
# Both right-hand profiles must agree.
def test_motors_four_and_five_drive_the_pinky():
    for profile in (ELEVEN_DOF_RIGHT, SIX_DOF_RIGHT):
        assert describe_motor(profile, 4) == ("pinky", "PIP")
        assert describe_motor(profile, 5) == ("pinky", "MCP")


def test_motors_ten_and_eleven_drive_the_index():
    for profile in (ELEVEN_DOF_RIGHT, SIX_DOF_RIGHT):
        assert describe_motor(profile, 10) == ("index", "PIP")
        assert describe_motor(profile, 11) == ("index", "MCP")


def test_swapping_ids_keeps_each_fingers_own_angle_tuning():
    """Only the ids move; min/max/default belong to the finger, not the motor."""
    index = SIX_DOF_RIGHT.fingers["index"].motors
    pinky = SIX_DOF_RIGHT.fingers["pinky"].motors

    assert (index["PIP"].motor_id, index["PIP"].default_deg) == (10, 45)
    assert (index["MCP"].motor_id, index["MCP"].default_deg) == (11, 30)
    assert (pinky["PIP"].motor_id, pinky["PIP"].default_deg) == (4, 35)
    assert (pinky["MCP"].motor_id, pinky["MCP"].default_deg) == (5, 45)


def test_motors_six_and_seven_drive_the_ring():
    for profile in (ELEVEN_DOF_RIGHT, SIX_DOF_RIGHT):
        assert describe_motor(profile, 6) == ("ring", "PIP")
        assert describe_motor(profile, 7) == ("ring", "MCP")


def test_motors_eight_and_nine_drive_the_middle():
    for profile in (ELEVEN_DOF_RIGHT, SIX_DOF_RIGHT):
        assert describe_motor(profile, 8) == ("middle", "PIP")
        assert describe_motor(profile, 9) == ("middle", "MCP")


def test_middle_and_ring_keep_their_own_angle_tuning():
    middle = SIX_DOF_RIGHT.fingers["middle"].motors
    ring = SIX_DOF_RIGHT.fingers["ring"].motors

    assert (middle["PIP"].motor_id, middle["PIP"].default_deg) == (8, 55)
    assert (middle["MCP"].motor_id, middle["MCP"].default_deg) == (9, 35)
    assert (ring["PIP"].motor_id, ring["PIP"].default_deg) == (6, 45)
    assert (ring["MCP"].motor_id, ring["MCP"].default_deg) == (7, 40)


def test_the_right_hand_chain_runs_from_pinky_to_index():
    """Every id maps to exactly one finger, in reversed chain order."""
    expected = {
        4: "pinky", 5: "pinky", 6: "ring", 7: "ring",
        8: "middle", 9: "middle", 10: "index", 11: "index",
    }
    for motor_id, finger in expected.items():
        assert describe_motor(ELEVEN_DOF_RIGHT, motor_id)[0] == finger
