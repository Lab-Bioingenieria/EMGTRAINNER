from unittest.mock import MagicMock, call

import dynamixel_sdk as dxl
import pytest

from app.core import dynamixel_interface as module
from app.core.dynamixel_interface import DynamixelInterface


def _interface() -> DynamixelInterface:
    interface = DynamixelInterface(port_name="/dev/ttyFAKE")
    interface.packet_handler = MagicMock()
    interface.set_operating_mode = MagicMock()
    interface.set_current_limit = MagicMock()
    interface.set_profile_velocity = MagicMock()
    interface.set_profile_acceleration = MagicMock()
    interface.enable_torque = MagicMock()
    interface.disable_torque = MagicMock()
    return interface


def _freeze_loop_time(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module.time, "time", MagicMock(return_value=0.0))
    monkeypatch.setattr(module.time, "sleep", MagicMock())


def test_single_motor_disables_torque_after_three_consecutive_overcurrent_samples(monkeypatch):
    interface = _interface()
    _freeze_loop_time(monkeypatch)
    interface.read_current_amps = MagicMock(return_value=module.MAX_CURRENT_A + 0.1)

    with pytest.raises(RuntimeError, match="Sobrecorriente"):
        interface.move_motor_safe(motor_id=1, goal_position=2048)

    assert interface.read_current_amps.call_count == 3
    interface.disable_torque.assert_called_once_with(1)


def test_sync_move_disables_motor_after_three_consecutive_overcurrent_samples(monkeypatch):
    interface = _interface()
    _freeze_loop_time(monkeypatch)
    interface.read_current_amps = MagicMock(return_value=module.MAX_CURRENT_A + 0.1)

    group = MagicMock()
    group.addParam.return_value = True
    group.txPacket.return_value = dxl.COMM_SUCCESS
    monkeypatch.setattr(module.dxl, "GroupSyncWrite", MagicMock(return_value=group))

    with pytest.raises(RuntimeError, match="Sobrecorriente"):
        interface.move_motors_sync_safe({1: 2048})

    assert interface.read_current_amps.call_count == 3
    interface.disable_torque.assert_called_once_with(1)


def test_single_motor_disables_torque_when_current_monitoring_fails(monkeypatch):
    interface = _interface()
    _freeze_loop_time(monkeypatch)
    interface.read_current_amps = MagicMock(side_effect=OSError("serial read failed"))

    with pytest.raises(RuntimeError, match="monitorear corriente"):
        interface.move_motor_safe(motor_id=1, goal_position=2048)

    interface.disable_torque.assert_called_once_with(1)


def test_sync_move_disables_all_targets_when_current_monitoring_fails(monkeypatch):
    interface = _interface()
    _freeze_loop_time(monkeypatch)
    monkeypatch.setattr(module.time, "time", MagicMock(side_effect=[0.0, 0.0, 2.0]))
    interface.read_current_amps = MagicMock(side_effect=OSError("serial read failed"))

    group = MagicMock()
    group.addParam.return_value = True
    group.txPacket.return_value = dxl.COMM_SUCCESS
    monkeypatch.setattr(module.dxl, "GroupSyncWrite", MagicMock(return_value=group))

    with pytest.raises(RuntimeError, match="monitorear corriente"):
        interface.move_motors_sync_safe({1: 2048, 2: 2048})

    assert interface.disable_torque.call_args_list == [call(1), call(2)]


def test_current_read_raises_on_sdk_transport_failure():
    interface = _interface()
    interface.packet_handler.read2ByteTxRx.return_value = (0, dxl.COMM_TX_FAIL, 0)
    interface.packet_handler.getTxRxResult.return_value = "COMM_TX_FAIL"

    with pytest.raises(RuntimeError, match="COMM_TX_FAIL"):
        interface.read_current_units(1)


def test_current_read_raises_on_dynamixel_packet_error():
    interface = _interface()
    interface.packet_handler.read2ByteTxRx.return_value = (0, dxl.COMM_SUCCESS, 4)
    interface.packet_handler.getRxPacketError.return_value = "DATA_RANGE_ERROR"

    with pytest.raises(RuntimeError, match="DATA_RANGE_ERROR"):
        interface.read_current_units(1)
