"""Port discovery must survive a stale config and never grab the wrong device."""
from types import SimpleNamespace

import pytest

from app.core import dynamixel_interface as di


def _port(device, vid=None, description="n/a", manufacturer=None):
    return SimpleNamespace(
        device=device, vid=vid, description=description, manufacturer=manufacturer
    )


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    """No real config, no real environment, no real filesystem."""
    monkeypatch.setattr(di.hardware_config, "main_port", None, raising=False)
    monkeypatch.delenv("DYNAMIXEL_PORT", raising=False)
    monkeypatch.setattr(di, "_list_serial_ports", lambda: [])
    monkeypatch.setattr(di.glob, "glob", lambda pattern: [])
    monkeypatch.setattr(di.os.path, "exists", lambda path: False)
    monkeypatch.setattr(di.os, "name", "posix")


# --- configured port is validated, not trusted blindly ---

def test_configured_port_is_used_when_it_exists(monkeypatch):
    monkeypatch.setattr(di.hardware_config, "main_port", "/dev/ttyUSB3", raising=False)
    monkeypatch.setattr(di.os.path, "exists", lambda path: path == "/dev/ttyUSB3")

    assert di.find_u2d2_port() == "/dev/ttyUSB3"


def test_stale_configured_port_falls_back_to_autodetection(monkeypatch):
    """The Jetson had main_port=/dev/ttyUSB1 while the adapter was on USB0."""
    monkeypatch.setattr(di.hardware_config, "main_port", "/dev/ttyUSB1", raising=False)
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [_port("/dev/ttyUSB0", vid=di.FTDI_VENDOR_ID, description="FT232H")],
    )

    assert di.find_u2d2_port() == "/dev/ttyUSB0"


def test_stale_env_port_falls_back_to_autodetection(monkeypatch):
    monkeypatch.setenv("DYNAMIXEL_PORT", "/dev/ttyUSB9")
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [_port("/dev/ttyUSB0", vid=di.FTDI_VENDOR_ID)],
    )

    assert di.find_u2d2_port() == "/dev/ttyUSB0"


def test_configured_port_wins_over_a_present_adapter(monkeypatch):
    monkeypatch.setattr(di.hardware_config, "main_port", "/dev/ttyUSB5", raising=False)
    monkeypatch.setattr(di.os.path, "exists", lambda path: path == "/dev/ttyUSB5")
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [_port("/dev/ttyUSB0", vid=di.FTDI_VENDOR_ID)],
    )

    assert di.find_u2d2_port() == "/dev/ttyUSB5"


# --- Linux (arm64 and amd64 behave identically here) ---

def test_linux_prefers_the_stable_by_id_symlink(monkeypatch):
    by_id = "/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_X-if00-port0"
    monkeypatch.setattr(di.glob, "glob", lambda pattern: [by_id])
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [_port("/dev/ttyUSB0", vid=di.FTDI_VENDOR_ID)],
    )

    assert di.find_u2d2_port() == by_id


def test_linux_falls_back_to_vendor_id_when_by_id_is_absent(monkeypatch):
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [_port("/dev/ttyUSB0", vid=di.FTDI_VENDOR_ID)],
    )

    assert di.find_u2d2_port() == "/dev/ttyUSB0"


def test_non_ftdi_devices_are_never_selected(monkeypatch):
    """The ESP32 sensor shares the bus; grabbing it would break both devices."""
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [
            _port("/dev/ttyUSB0", vid=0x10C4, description="CP2102 USB to UART"),
            _port("/dev/ttyS0"),
        ],
    )

    assert di.find_u2d2_port() is None


def test_description_identifies_ftdi_when_the_vendor_id_is_missing(monkeypatch):
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [_port("/dev/ttyUSB0", vid=None, manufacturer="FTDI")],
    )

    assert di.find_u2d2_port() == "/dev/ttyUSB0"


def test_multiple_adapters_resolve_deterministically(monkeypatch):
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [
            _port("/dev/ttyUSB2", vid=di.FTDI_VENDOR_ID),
            _port("/dev/ttyUSB0", vid=di.FTDI_VENDOR_ID),
        ],
    )

    assert di.find_u2d2_port() == "/dev/ttyUSB0"


# --- Windows ---

def test_windows_validates_a_com_port_through_the_port_list(monkeypatch):
    """COM names are not filesystem paths, so os.path.exists cannot check them."""
    monkeypatch.setattr(di.os, "name", "nt")
    monkeypatch.setattr(di.hardware_config, "main_port", "COM4", raising=False)
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [_port("COM4", vid=di.FTDI_VENDOR_ID, description="USB Serial Port")],
    )

    assert di.find_u2d2_port() == "COM4"


def test_windows_stale_com_port_falls_back_to_the_real_adapter(monkeypatch):
    monkeypatch.setattr(di.os, "name", "nt")
    monkeypatch.setattr(di.hardware_config, "main_port", "COM9", raising=False)
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [_port("COM3", vid=di.FTDI_VENDOR_ID, description="USB Serial Port")],
    )

    assert di.find_u2d2_port() == "COM3"


def test_windows_never_returns_an_arbitrary_port(monkeypatch):
    """The old code returned ports[0], which could be Bluetooth or a legacy COM."""
    monkeypatch.setattr(di.os, "name", "nt")
    monkeypatch.setattr(
        di, "_list_serial_ports",
        lambda: [
            _port("COM1", description="Communications Port"),
            _port("COM5", vid=0x0A5C, description="Standard Serial over Bluetooth"),
        ],
    )

    assert di.find_u2d2_port() is None


def test_windows_does_not_glob_the_posix_device_tree(monkeypatch):
    monkeypatch.setattr(di.os, "name", "nt")

    def _fail(pattern):
        raise AssertionError(f"globbed {pattern} on Windows")

    monkeypatch.setattr(di.glob, "glob", _fail)
    monkeypatch.setattr(di, "_list_serial_ports", lambda: [])

    assert di.find_u2d2_port() is None


def test_nothing_connected_returns_none():
    assert di.find_u2d2_port() is None
