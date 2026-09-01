"""Saving a port from the web UI must recycle the hand connections.

The operator picks the new USB port in the frontend's hardware-config module.
If the running services keep their old handles, the save looks successful but
the hand stays dead (or keeps writing to a stale /dev/ttyUSBn) until the
backend is restarted.
"""
import importlib

hm = importlib.import_module("api.v1.microcontrollers.health_micro")
es = importlib.import_module("app.services.emg_service")

from app.schemas.hardware import HardwareConfigUpdate
from app.services.hand_service import HandService


def test_config_save_recycles_hand_connections(monkeypatch):
    saved = {}

    class FakeConfig:
        def save_config(self, main_port=None, independent_data_acquisition=False,
                        data_port=None, sensor_type="umyo", motor_type="dynamixels"):
            saved["main_port"] = main_port

        def get_config(self):
            return dict(saved)

    monkeypatch.setattr(hm, "hardware_config", FakeConfig())

    calls = []
    monkeypatch.setattr(es.emg_service, "disconnect_hand", lambda: calls.append("emg"))
    monkeypatch.setattr(HandService, "release_hardware", lambda self: calls.append("hand"))

    hm.update_config(HardwareConfigUpdate(main_port="/dev/ttyUSB9"))

    assert saved["main_port"] == "/dev/ttyUSB9"
    assert calls == ["emg", "hand"]
