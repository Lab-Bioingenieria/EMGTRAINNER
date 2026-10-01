import importlib.util
import os
import random

_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "app", "services", "gesture_classifier.py")
_spec = importlib.util.spec_from_file_location("gesture_classifier", _PATH)
gc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gc)


def _blob(center, spread, n, seed):
    rng = random.Random(seed)
    return [[center[i] + rng.uniform(-spread, spread) for i in range(len(center))] for _ in range(n)]


def test_separates_two_well_separated_gaussian_blobs():
    X = _blob([0, 0], 1, 80, 1) + _blob([10, 10], 1, 80, 2)
    y = ["A"] * 80 + ["B"] * 80
    clf = gc.GaussianNBClassifier()
    clf.fit(X, y, ["f1", "f2"])

    label, conf = clf.predict([0.2, -0.3])
    assert label == "A" and conf > 0.9
    label, conf = clf.predict([9.8, 10.1])
    assert label == "B" and conf > 0.9


def test_predict_proba_sums_to_one_and_covers_all_classes():
    clf = gc.GaussianNBClassifier()
    clf.fit([[0.0], [1.0], [5.0]], ["rest", "rest", "move"], ["f1"])
    proba = clf.predict_proba([0.5])
    assert set(proba) == {"rest", "move"}
    assert abs(sum(proba.values()) - 1.0) < 1e-9


def test_constant_feature_does_not_crash_with_zero_variance():
    clf = gc.GaussianNBClassifier()
    clf.fit([[1.0, 5.0], [1.0, 6.0], [1.0, 50.0]], ["a", "a", "b"], ["const", "varies"])
    label, conf = clf.predict([1.0, 5.5])
    assert label == "a" and 0.0 <= conf <= 1.0


def _alternating(mean, half_spread, n, dims):
    """n puntos deterministicos con media y varianza exactas (sin azar): alterna
    ``mean +/- half_spread`` en cada dimension, dando varianza = half_spread**2."""
    return [[mean + (half_spread if i % 2 == 0 else -half_spread)] * dims for i in range(n)]


def test_shared_variance_stops_a_tight_small_class_from_hijacking_predictions():
    # "wide" es la clase grande y dispersa (media 0, varianza 4 en cada dimension).
    # "tight" tiene pocas ventanas y resulto mas homogenea (media 0.2, varianza 0.01):
    # este es el fallo real que se vio entrenando con las sesiones guardadas, donde la
    # clase "cerrar" (mas homogenea entre sesiones, no mas facil de distinguir) se
    # comia casi todas las predicciones de prueba y la exactitud caia por debajo de
    # adivinar al azar.
    dims = 6
    wide = _alternating(0.0, 2.0, 200, dims)
    tight = _alternating(0.2, 0.1, 20, dims)
    X, y = wide + tight, ["wide"] * len(wide) + ["tight"] * len(tight)
    names = [f"f{i}" for i in range(dims)]

    shared = gc.GaussianNBClassifier()
    shared.fit(X, y, names, shared_variance=True)
    unshared = gc.GaussianNBClassifier()
    unshared.fit(X, y, names, shared_variance=False)

    # En la propia media de "wide" (el punto mas favorable posible para "wide"):
    # sin varianza compartida, la campana angosta de "tight" gana igual.
    at_wide_mean = [0.0] * dims
    assert unshared.predict(at_wide_mean)[0] == "tight"
    assert shared.predict(at_wide_mean)[0] == "wide"


def test_roundtrip_through_dict_gives_identical_predictions():
    X = _blob([0, 0], 1, 40, 3) + _blob([8, -8], 1, 40, 4) + _blob([-8, 8], 1, 40, 5)
    y = ["reposo"] * 40 + ["cerrar"] * 40 + ["abrir"] * 40
    clf = gc.GaussianNBClassifier()
    clf.fit(X, y, ["f1", "f2"])

    restored = gc.GaussianNBClassifier.from_dict(clf.to_dict())
    for point in ([0.1, 0.1], [7.5, -7.9], [-8.2, 8.1]):
        assert clf.predict(point) == restored.predict(point)
    assert restored.classes_ == clf.classes_ and restored.feature_names == clf.feature_names


def test_fit_rejects_mismatched_lengths_and_empty_input():
    clf = gc.GaussianNBClassifier()
    try:
        clf.fit([[1.0]], ["a", "b"], ["f1"])
        assert False
    except ValueError:
        pass
    try:
        clf.fit([], [], ["f1"])
        assert False
    except ValueError:
        pass


def test_predict_before_fit_raises():
    clf = gc.GaussianNBClassifier()
    assert not clf.is_fitted
    try:
        clf.predict([1.0])
        assert False
    except RuntimeError:
        pass
