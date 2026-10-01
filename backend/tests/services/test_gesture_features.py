import importlib.util
import os

_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "app", "services", "gesture_features.py")
_spec = importlib.util.spec_from_file_location("gesture_features", _PATH)
gf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gf)


def test_feature_names_match_window_features_length():
    window = [(500.0, 500.0, 500.0)] * gf.WINDOW_SIZE
    feats = gf.window_features(window, (500.0, 500.0, 500.0))
    assert len(feats) == len(gf.FEATURE_NAMES) == 12


def test_rest_window_is_near_one_with_low_std_and_flat_slope():
    window = [(505.0, 498.0, 500.0), (495.0, 502.0, 500.0)] * 5
    feats = gf.window_features(window, (500.0, 500.0, 500.0))
    means = feats[0::4]
    stds = feats[2::4]
    slopes = feats[3::4]
    assert all(abs(m - 1.0) < 0.05 for m in means)
    assert all(s < 0.05 for s in stds)
    assert all(abs(s) < 0.02 for s in slopes)


def test_strong_contraction_doubles_the_relative_mean_on_that_channel():
    window = [(1000.0, 500.0, 500.0)] * 10
    feats = gf.window_features(window, (500.0, 500.0, 500.0))
    assert feats[0] == 2.0     # ch1 mean/reposo
    assert feats[4] == 1.0     # ch2 sin cambios
    assert feats[8] == 1.0     # ch3 sin cambios


def test_slope_is_positive_when_rising_and_negative_when_falling():
    rising = [(100.0, 0, 0)] * 3 + [(400.0, 0, 0)] * 3 + [(900.0, 0, 0)] * 3
    falling = list(reversed(rising))
    up = gf.window_features(rising, (100.0, 1.0, 1.0))
    down = gf.window_features(falling, (100.0, 1.0, 1.0))
    assert up[3] > 0.5
    assert down[3] < -0.5


def test_window_features_handles_empty_window_and_zero_baseline():
    assert gf.window_features([], (500.0, 500.0, 500.0)) == [0.0] * 12
    # baseline 0 (canal sin calibrar): se usa 1.0 en su lugar, sin dividir por cero.
    feats = gf.window_features([(100.0, 0.0, 0.0)], (0.0, 0.0, 0.0))
    assert feats[0] == 100.0 and feats[4] == 0.0


def test_rolling_window_only_reports_ready_once_full_and_uses_last_n_samples():
    rw = gf.RollingWindow(size=4)
    assert not rw.ready
    for v in (100.0, 200.0, 300.0):
        rw.push((v, v, v))
    assert not rw.ready
    rw.push((400.0, 400.0, 400.0))
    assert rw.ready
    feats = rw.features((100.0, 100.0, 100.0))
    assert feats[0] == (100 + 200 + 300 + 400) / 4 / 100   # las 4 ultimas, no mas
    rw.push((500.0, 500.0, 500.0))   # empuja la mas vieja (100) fuera
    feats2 = rw.features((100.0, 100.0, 100.0))
    assert feats2[0] == (200 + 300 + 400 + 500) / 4 / 100
