from unittest.mock import MagicMock

import dynamixel_sdk as dxl

from app.core.dynamixel_interface import (
    DynamixelInterface,
    PROTOCOL_VERSION,
    inventory_report,
    resolve_model_name,
)


def _build_interface_with_mocked_bus() -> DynamixelInterface:
    dx = DynamixelInterface(port_name="/dev/ttyFAKE", baudrate=1000000)
    dx.packet_handler = MagicMock()
    return dx


def test_resolve_model_name_maps_known_robotis_numbers():
    assert resolve_model_name(1190) == "XL330-M077-T"
    assert resolve_model_name(1200) == "XL330-M288-T"


def test_resolve_model_name_returns_unknown_for_unmapped_number():
    assert resolve_model_name(9999) == "UNKNOWN"


def test_inventory_reports_responding_ids_model_numbers_and_names():
    dx = _build_interface_with_mocked_bus()

    def fake_ping(port_handler, motor_id):
        if motor_id == 1:
            return 1190, dxl.COMM_SUCCESS, 0
        if motor_id == 2:
            return 1200, dxl.COMM_SUCCESS, 0
        return 0, dxl.COMM_TX_FAIL, 0

    dx.packet_handler.ping.side_effect = fake_ping

    result = dx.inventory(id_range=range(1, 4))

    assert result == [
        {"id": 1, "model_number": 1190, "model_name": "XL330-M077-T"},
        {"id": 2, "model_number": 1200, "model_name": "XL330-M288-T"},
    ]


def test_inventory_reports_unknown_model_name_for_unmapped_number():
    dx = _build_interface_with_mocked_bus()
    dx.packet_handler.ping.return_value = (9999, dxl.COMM_SUCCESS, 0)

    result = dx.inventory(id_range=range(1, 2))

    assert result == [{"id": 1, "model_number": 9999, "model_name": "UNKNOWN"}]


def test_inventory_uses_ping_result_directly_without_a_second_register_read():
    dx = _build_interface_with_mocked_bus()
    dx.packet_handler.ping.return_value = (1200, dxl.COMM_SUCCESS, 0)

    dx.inventory(id_range=range(1, 2))

    dx.packet_handler.read2ByteTxRx.assert_not_called()


def test_inventory_never_enables_torque_or_writes_registers():
    dx = _build_interface_with_mocked_bus()
    dx.packet_handler.ping.return_value = (1200, dxl.COMM_SUCCESS, 0)

    dx.inventory(id_range=range(1, 2))

    dx.packet_handler.write1ByteTxRx.assert_not_called()
    dx.packet_handler.write2ByteTxRx.assert_not_called()
    dx.packet_handler.write4ByteTxRx.assert_not_called()


def test_inventory_scans_every_id_used_by_supported_profiles_by_default():
    dx = _build_interface_with_mocked_bus()
    dx.packet_handler.ping.return_value = (0, dxl.COMM_TX_FAIL, 0)

    dx.inventory()

    assert [call.args[1] for call in dx.packet_handler.ping.call_args_list] == list(range(1, 16))


def test_inventory_report_includes_port_protocol_and_baudrate():
    dx = _build_interface_with_mocked_bus()
    dx.packet_handler.ping.return_value = (1200, dxl.COMM_SUCCESS, 0)

    report = inventory_report(dx, id_range=range(1, 2))

    assert report == {
        "port": "/dev/ttyFAKE",
        "protocol_version": PROTOCOL_VERSION,
        "baudrate": 1000000,
        "motors": [{"id": 1, "model_number": 1200, "model_name": "XL330-M288-T"}],
    }
