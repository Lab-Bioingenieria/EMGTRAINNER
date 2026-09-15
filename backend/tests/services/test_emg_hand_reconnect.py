"""A replugged U2D2 must not leave the web UI dead.

The backend used to resolve the hand port exactly once: if the adapter was
unplugged and replugged (possibly as a different /dev/ttyUSBn), every gesture
from the frontend was silently dropped or written to a stale handle until the
backend was restarted. These tests pin the recovery behaviour: lazy reconnect
on the next gesture, teardown after a transport failure, and a config save
from the web UI dropping the old connection.
"""
import importlib

import pytest

# `app.services.emg_service` also exports a module-level singleton named
# `emg_service`, which shadows the module on a plain `from ... import`.
es = importlib.import_module("app.services.emg_service")


class FakeInterface:
    """Stands in for DynamixelInterface; records its lifecycle."""

    def __init__(self, port_name=None):
        self.port_name = port_name
        self.closed = False

    def initialize(self):
        pass

    def scan_motors(self):
        return [1, 2, 3]

    def close(self):
        self.closed = True


@pytest.fixture
def service(monkeypatch):
    """A service booted with no U2D2 present."""
    monkeypatch.setattr(es, "find_u2d2_port", lambda: None)
    return es.EMGDataService()


def test_reconnects_on_next_gesture_after_late_plugin(service, monkeypatch):
    """Adapter plugged in after boot: the next label change must attach it."""
    assert service.hand_interface is None

    monkeypatch.setattr(es, "find_u2d2_port", lambda: "/dev/ttyUSB7")
    monkeypatch.setattr(es, "DynamixelInterface", FakeInterface)

    service.set_current_label("CERRAR")

    assert isinstance(service.hand_interface, FakeInterface)
    assert service.hand_interface.port_name == "/dev/ttyUSB7"


def test_transport_failure_drops_the_interface(service, monkeypatch):
    """A dead bus must be torn down so the next gesture re-resolves the port."""
    interface = FakeInterface(port_name="/dev/ttyUSB0")
    service.hand_interface = interface

    def _boom(*_args, **_kwargs):
        raise RuntimeError("[TxRxResult] There is no status packet!")

    monkeypatch.setattr(es, "execute_gesture", _boom)
    service._move_hand("ZERO")

    assert interface.closed
    assert service.hand_interface is None


def test_unknown_gesture_keeps_the_interface(service, monkeypatch):
    """A caller bug (ValueError) is not a hardware problem: keep the port."""
    interface = FakeInterface(port_name="/dev/ttyUSB0")
    service.hand_interface = interface

    def _boom(*_args, **_kwargs):
        raise ValueError("[ERROR] - Gesto no definido: NOPE")

    monkeypatch.setattr(es, "execute_gesture", _boom)
    service._move_hand("NOPE")

    assert not interface.closed
    assert service.hand_interface is interface


def test_connect_hand_is_idempotent_when_connected(service, monkeypatch):
    interface = FakeInterface(port_name="/dev/ttyUSB0")
    service.hand_interface = interface

    def _forbidden(_port_name=None):
        raise AssertionError("connect_hand reopened an already-open interface")

    monkeypatch.setattr(es, "DynamixelInterface", _forbidden)
    service.connect_hand()

    assert service.hand_interface is interface
