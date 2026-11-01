"""Pruebas de la logica pura de calibracion del Espejo en Tiempo Real."""
import random

import pytest

from app.services.mirror_calibration import (
    CalibrationError,
    MirrorCalibration,
    build_channel_calibration,
)


def _noisy(center: float, spread: float, n: int, seed: int = 0):
    rng = random.Random(seed)
    return [center + rng.uniform(-spread, spread) for _ in range(n)]


def test_channel_maps_rest_to_zero_and_strong_contraction_to_one():
    rest = _noisy(100, 5, 150)
    contract = _noisy(900, 40, 120)
    cal = build_channel_calibration(rest, contract)

    assert cal.normalize(100) == 0.0          # reposo: zona muerta
    assert cal.normalize(cal.floor) == 0.0
    assert cal.normalize(cal.ceil) == pytest.approx(1.0)
    assert cal.normalize(10_000) == 1.0       # satura, no pasa de 1
    assert 0.0 < cal.normalize((cal.floor + cal.ceil) / 2) < 1.0


def test_deadband_absorbs_rest_noise():
    rest = _noisy(100, 5, 200, seed=1)
    cal = build_channel_calibration(rest, _noisy(900, 40, 120, seed=2))
    # Ninguna muestra de reposo debe mover la mano.
    assert all(cal.normalize(v) == 0.0 for v in rest)


def test_flat_rest_still_gets_a_minimum_deadband():
    # Reposo casi sin ruido: la zona muerta no puede quedar en cero.
    cal = build_channel_calibration([100.0] * 50, [800.0] * 50)
    assert cal.floor > 100.0


def test_weak_contraction_is_rejected():
    with pytest.raises(CalibrationError):
        build_channel_calibration(_noisy(100, 5, 100), _noisy(110, 5, 100))


def test_too_few_samples_is_rejected():
    with pytest.raises(CalibrationError):
        build_channel_calibration([100.0] * 3, [900.0] * 3)


def test_channels_are_calibrated_independently():
    # Sensor 0 de ganancia baja, sensor 1 de ganancia alta: con el mismo
    # esfuerzo relativo deben dar el mismo valor normalizado.
    c0 = build_channel_calibration(_noisy(50, 2, 100), _noisy(400, 20, 100))
    c1 = build_channel_calibration(_noisy(500, 20, 100), _noisy(4000, 200, 100))
    cal = MirrorCalibration([c0, c1, None])

    mid0 = (c0.floor + c0.ceil) / 2
    mid1 = (c1.floor + c1.ceil) / 2
    levels = cal.normalize([mid0, mid1, 999.0])

    assert levels[0] == pytest.approx(levels[1])
    assert levels[2] == 0.0                   # canal sin sensor
    assert cal.activation([c0.ceil, 0.0, 0.0]) == pytest.approx(1.0)


def test_activation_is_zero_at_rest_and_handles_missing_values():
    c0 = build_channel_calibration(_noisy(100, 5, 100), _noisy(900, 40, 100))
    cal = MirrorCalibration([c0, None, None])
    assert cal.activation([100.0, 0.0, 0.0]) == 0.0
    assert cal.normalize([]) == [0.0, 0.0, 0.0]   # muestra corta: sin excepcion
    assert cal.to_list()[1] is None


def test_rest_spikes_do_not_inflate_the_deadband():
    # Picos aislados enormes (como los que manda el ESP32) no deben subir el
    # umbral: el reposo se resume con mediana y MAD, no con media y desviacion.
    rest = _noisy(500, 20, 150, seed=3)
    for i in (10, 47, 90, 133):
        rest[i] = 25_000.0
    cal = build_channel_calibration(rest, _noisy(1500, 80, 100, seed=4))

    assert 500 < cal.floor < 700
    assert cal.rest_level == pytest.approx(500, abs=15)


def test_weak_error_message_reports_the_measured_levels():
    with pytest.raises(CalibrationError) as exc:
        build_channel_calibration(_noisy(500, 10, 100), _noisy(520, 10, 100))
    msg = str(exc.value)
    assert "reposo" in msg and "contracción" in msg and "haría falta" in msg


def _long_tail(median: float, cv: float, n: int, seed: int):
    """Ruido de cola larga (log-normal) como el del sensor real: ~40 % del nivel."""
    rng = random.Random(seed)
    return [median * rng.lognormvariate(0, cv) for _ in range(n)]


def test_noisy_real_world_signal_passes_when_contraction_is_clearly_higher():
    # Reposo ~500 con 40 % de ruido; agarre fuerte ~1.8x. Antes (piso = reposo + 2.5 sigma)
    # esto se rechazaba siempre porque el piso quedaba por encima de la contraccion.
    rest = _long_tail(500, 0.4, 150, seed=5)
    cal = build_channel_calibration(rest, _long_tail(900, 0.4, 150, seed=6))
    assert cal.separation >= 0.5
    assert cal.floor < cal.ceil
    # En reposo la mano casi no se mueve.
    assert sum(cal.normalize(v) > 0.2 for v in rest) / len(rest) < 0.15


def test_contraction_buried_in_rest_noise_is_still_rejected():
    # Un "puño" que no cambia el nivel medio respecto al reposo no debe calibrarse.
    with pytest.raises(CalibrationError) as exc:
        build_channel_calibration(
            _long_tail(500, 0.4, 150, seed=7), _long_tail(520, 0.4, 150, seed=8)
        )
    assert "ruido" in str(exc.value)


def test_to_dict_reports_separation():
    cal = build_channel_calibration(_noisy(100, 5, 100), _noisy(900, 40, 100))
    assert cal.to_dict()["separation"] == 1.0
