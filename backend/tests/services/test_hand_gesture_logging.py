"""A failed gesture must report why it failed.

`move_motors_sync_safe` raises a RuntimeError that names the motor but chains
the real transport error as `__cause__`. The service used to print only the
outer message, so an operator saw "torque deshabilitado en el grupo" with no
way to tell a jammed joint from a stolen serial reply.
"""
import importlib

import pytest

# `app.services.emg_service` also exports a module-level singleton named
# `emg_service`, which shadows the module on a plain `from ... import`.
es = importlib.import_module("app.services.emg_service")


@pytest.fixture
def service(monkeypatch):
    """A service with no hardware attached."""
    monkeypatch.setattr(es, "find_u2d2_port", lambda: None)
    instance = es.EMGDataService()
    instance.hand_interface = object()
    return instance


def test_chained_cause_is_reported(service, monkeypatch, capsys):
    cause = RuntimeError("[TxRxResult] There is no status packet!")
    outer = RuntimeError("[ERROR] - No se pudo monitorear corriente del motor 10")
    outer.__cause__ = cause

    def _boom(*_args, **_kwargs):
        raise outer

    monkeypatch.setattr(es, "execute_gesture", _boom)
    service._move_hand("ZERO")

    printed = capsys.readouterr().out
    assert "motor 10" in printed
    assert "no status packet" in printed.lower(), (
        f"the root cause was swallowed: {printed!r}"
    )


def test_plain_failure_still_reported(service, monkeypatch, capsys):
    def _boom(*_args, **_kwargs):
        raise ValueError("[ERROR] - Gesto no definido: NOPE")

    monkeypatch.setattr(es, "execute_gesture", _boom)
    service._move_hand("NOPE")

    assert "Gesto no definido" in capsys.readouterr().out


def test_success_is_not_treated_as_failure(service, monkeypatch, capsys):
    monkeypatch.setattr(es, "execute_gesture", lambda *a, **k: None)
    service._move_hand("ZERO")

    assert "Error" not in capsys.readouterr().out
