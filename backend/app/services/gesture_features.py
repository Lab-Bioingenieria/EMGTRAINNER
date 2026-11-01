"""Extraccion de caracteristicas para el clasificador de movimientos (dedos y gestos).

Por que estas caracteristicas y no las "clasicas" de EMG
----------------------------------------------------------
La bibliografia de control mioelectrico (Hudgins et al.) extrae caracteristicas
como cruces por cero o cambios de signo de la pendiente sobre la senal cruda de
EMG, que oscila alrededor de cero. Los sensores uMyo de este proyecto NO mandan
eso: mandan un "muscle level" ya rectificado (una envolvente, siempre positiva,
ver ``emg_cleaning``). Cruces por cero no aplican a una senal que nunca cruza
cero. En su lugar, por canal y por ventana se usan caracteristicas pensadas para
una envolvente:

- ``mean``: nivel medio de la ventana, relativo al reposo de esa sesion/persona
  (``valor / reposo``; 1.0 = igual que el reposo). La relativizacion es la que
  permite comparar entre sensores de distinta ganancia y entre sesiones/personas
  (ver ``mirror_calibration`` y el estudio de calibracion, que usan la misma idea).
- ``max``: pico de la ventana, relativo al reposo (agarra contracciones breves
  que el promedio diluye).
- ``std``: variabilidad dentro de la ventana, relativa al reposo (una
  contraccion sostenida es mas estable que el ruido de reposo).
- ``slope``: tendencia dentro de la ventana (tercio final menos tercio inicial,
  relativo al reposo): positiva si la fuerza esta subiendo, negativa si esta
  bajando, ~0 en reposo o en meseta.

Se calculan sobre la senal ya limpia (``clean1..3``: mediana + EMA, ver
``emg_cleaning``), nunca sobre la cruda, porque asi es como la usan tanto el
espejo como la calibracion, y asi debe alimentarse tambien la clasificacion en
vivo (misma canalizacion en entrenamiento y en inferencia).

Es logica pura (stdlib, sin numpy): los volumenes de este proyecto (miles de
ventanas) no lo justifican, y evita sumar una dependencia pesada solo para esto.
"""
from __future__ import annotations

import statistics
from typing import List, Sequence, Tuple

N_CHANNELS = 3
PER_CHANNEL_FEATURES = ("mean", "max", "std", "slope")
FEATURE_NAMES: List[str] = [
    f"ch{c + 1}_{name}" for c in range(N_CHANNELS) for name in PER_CHANNEL_FEATURES
]

# --- Ventaneo (compartido por el entrenamiento offline y la inferencia en vivo) ---
WINDOW_SIZE = 15   # lecturas por ventana (~0.5-0.9 s a 17-30 Hz, la tasa medida del sensor)
STEP = 8            # avance entre ventanas al entrenar (solapadas): mas ventanas por sesion
SETTLE_ROWS = 20    # lecturas a descartar al inicio de cada bloque (sube/baja la fuerza)

Sample = Tuple[float, float, float]


def _safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0


def window_features(window: Sequence[Sample], baseline: Sample) -> List[float]:
    """Vector de ``FEATURE_NAMES`` para una ventana de muestras limpias (ch1, ch2, ch3).

    ``baseline`` es el nivel de reposo de cada canal (de la calibracion vigente,
    o de la propia sesion al entrenar); nunca 0 en uso real, pero se protege
    igual por si un canal no tiene calibracion.
    """
    n = len(window)
    if n == 0:
        return [0.0] * len(FEATURE_NAMES)
    third = max(1, n // 3)
    out: List[float] = []
    for c in range(N_CHANNELS):
        vals = [w[c] for w in window]
        base = baseline[c] or 1.0
        mean = statistics.fmean(vals)
        peak = max(vals)
        std = statistics.pstdev(vals) if n > 1 else 0.0
        slope = statistics.fmean(vals[-third:]) - statistics.fmean(vals[:third])
        out.extend([_safe_div(mean, base), _safe_div(peak, base), _safe_div(std, base), _safe_div(slope, base)])
    return out


class RollingWindow:
    """Ventana deslizante de las ultimas ``WINDOW_SIZE`` muestras limpias, para inferencia en vivo.

    Solo avanza con lecturas *nuevas* del sensor (igual criterio que ``emg_cleaning``
    y los grabadores: una linea repetida del ESP32 no cuenta como muestra nueva).
    """

    def __init__(self, size: int = WINDOW_SIZE) -> None:
        self.size = size
        self._buf: List[Sample] = []

    def push(self, sample: Sample) -> None:
        self._buf.append(sample)
        if len(self._buf) > self.size:
            self._buf.pop(0)

    @property
    def ready(self) -> bool:
        return len(self._buf) >= self.size

    def features(self, baseline: Sample) -> List[float]:
        return window_features(self._buf, baseline)
