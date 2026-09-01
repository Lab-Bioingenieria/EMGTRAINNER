"""The sEMG sensor must never open the Dynamixel adapter.

The U2D2 reports itself over USB as manufacturer "FTDI" with product
"USB <-> Serial Converter". pyserial exposes the product string as
`description` and `USB VID:PID=0403:6014 ...` as `hwid`, so neither field
contains the literal text "FTDI" -- only `manufacturer` and the vendor id do.
A substring filter over description/hwid therefore misses the adapter and the
generic "USB" fallback matches its product string, handing the sensor the
robotic hand's bus.
"""
from types import SimpleNamespace

import pytest

from core.serial import manager as sm


def _port(device, vid=None, description="n/a", manufacturer=None, hwid="n/a"):
    return SimpleNamespace(
        device=device,
        vid=vid,
        description=description,
        manufacturer=manufacturer,
        hwid=hwid,
    )


def _u2d2(device="/dev/ttyUSB0"):
    """The real U2D2 as pyserial reports it on Linux."""
    return _port(
        device,
        vid=0x0403,
        description="USB <-> Serial Converter",
        manufacturer="FTDI",
        hwid="USB VID:PID=0403:6014 SER=FTAO520W LOCATION=1-2.1",
    )


def _esp32(device="/dev/ttyUSB1"):
    return _port(
        device,
        vid=0x10C4,
        description="CP2102 USB to UART Bridge Controller",
        manufacturer="Silicon Labs",
        hwid="USB VID:PID=10C4:EA60 SER=0001 LOCATION=1-2.2",
    )


@pytest.fixture
def bus(monkeypatch):
    def _install(ports):
        monkeypatch.setattr(sm, "_list_serial_ports", lambda: ports)
    return _install


# --- the regression that stopped the hand from moving ---

def test_u2d2_alone_is_never_selected(bus):
    """With only the hand plugged in, the sensor must find nothing."""
    bus([_u2d2()])

    assert SerialManagerPort() is None


def test_u2d2_is_not_matched_by_the_generic_usb_fallback(bus):
    """Its product string contains "USB", which the fallback searches for."""
    bus([_u2d2()])

    assert sm.SerialManager().find_device_port(
        identifier="USB", excluded_identifiers=["FTDI"]
    ) is None


def test_esp32_is_selected_when_both_are_present(bus):
    bus([_u2d2(), _esp32()])

    assert SerialManagerPort() == "/dev/ttyUSB1"


def test_ftdi_recognised_by_vendor_id_alone(bus):
    """Descriptors can be blank; the vendor id still identifies the adapter."""
    bus([_port("/dev/ttyUSB0", vid=0x0403, description="n/a", hwid="n/a")])

    assert SerialManagerPort() is None


def test_ftdi_recognised_by_manufacturer_when_vid_is_missing(bus):
    bus([_port("/dev/ttyUSB0", description="USB <-> Serial Converter",
               manufacturer="FTDI", hwid="n/a")])

    assert SerialManagerPort() is None


def test_connect_refuses_to_open_the_hand_bus(bus):
    """connect() must fail loudly rather than seize the Dynamixel port."""
    bus([_u2d2()])
    opened = []

    class _Boom:
        def __init__(self, **kwargs):
            opened.append(kwargs.get("port"))

    import serial as pyserial
    original = pyserial.Serial
    pyserial.Serial = _Boom
    try:
        with pytest.raises(Exception):
            sm.SerialManager().connect()
    finally:
        pyserial.Serial = original

    assert opened == [], f"opened the Dynamixel bus: {opened}"


def test_explicit_port_is_still_respected(bus):
    """An operator naming a port keeps control; only autodetection is filtered."""
    bus([_u2d2()])
    opened = []

    class _Fake:
        def __init__(self, **kwargs):
            opened.append(kwargs.get("port"))
            self.is_open = True

    import serial as pyserial
    original = pyserial.Serial
    pyserial.Serial = _Fake
    try:
        assert sm.SerialManager().connect("/dev/ttyUSB0") is True
    finally:
        pyserial.Serial = original

    assert opened == ["/dev/ttyUSB0"]


def SerialManagerPort():
    """Autodetection result of a fresh manager."""
    return sm.SerialManager().autodetect_sensor_port()
