"""Pruebas del filtro de picos + suavizado de la senal cruda."""
import pytest

from app.services.emg_cleaning import ChannelCleaner, SignalCleaner


def _run(cleaner, values):
    return [cleaner.update(v) for v in values]


def test_isolated_spike_is_rejected():
    out = _run(ChannelCleaner(), [500, 510, 495, 505, 500, 30_000, 502, 498, 501, 499])
    assert max(out) < 600            # el pico de 30000 no llega a la salida


def test_two_reading_spike_is_rejected():
    out = _run(ChannelCleaner(), [500, 510, 495, 505, 500, 30_000, 25_000, 502, 498, 501])
    assert max(out) < 600


def test_sustained_rise_is_followed_not_clipped():
    # Una contraccion real sube durante muchas lecturas: la salida debe llegar arriba.
    out = _run(ChannelCleaner(), [500] * 6 + [1500 + i for i in range(20)])
    assert out[-1] > 1300


def test_repeated_lines_do_not_advance_the_window():
    # El ESP32 repite lineas mas rapido de lo que el sensor entrega lecturas:
    # un pico repetido 3 veces sigue siendo UNA lectura y debe rechazarse.
    c = ChannelCleaner()
    _run(c, [500, 510, 495, 505, 500])
    out = _run(c, [30_000, 30_000, 30_000])
    assert max(out) < 600


def test_signal_cleaner_is_per_channel():
    sc = SignalCleaner(3)
    frames = [(500 + d, 700 - d, 900 + d) for d in (0, 4, -3, 2, -1, 3)]
    frames += [(30_000, 705, 898)]                       # pico solo en el canal 0
    frames += [(500 + d, 700 - d, 900 + d) for d in (1, -2, 3, 0, -1)]
    last = None
    for f in frames:
        last = sc.update(f)
    assert last == pytest.approx((500, 700, 900), abs=10)
