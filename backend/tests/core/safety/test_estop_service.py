import pytest

from core.safety.estop import EmergencyStopEngaged, EmergencyStopService


@pytest.fixture
def estop() -> EmergencyStopService:
    return EmergencyStopService()


def test_estop_defaults_to_engaged(estop):
    assert estop.is_engaged is True


def test_assert_movement_allowed_raises_while_engaged(estop):
    with pytest.raises(EmergencyStopEngaged):
        estop.assert_movement_allowed()


def test_reset_disengages_and_allows_movement(estop):
    estop.reset(actor="tester")

    assert estop.is_engaged is False
    estop.assert_movement_allowed()


def test_engage_after_reset_blocks_movement_again(estop):
    estop.reset(actor="tester")
    estop.engage(reason="operator pressed e-stop", actor="tester")

    assert estop.is_engaged is True
    assert estop.state()["reason"] == "operator pressed e-stop"
    with pytest.raises(EmergencyStopEngaged):
        estop.assert_movement_allowed()


def test_state_exposes_engaged_flag_and_actor(estop):
    estop.reset(actor="tester")

    state = estop.state()
    assert state["engaged"] is False
    assert state["actor"] == "tester"
