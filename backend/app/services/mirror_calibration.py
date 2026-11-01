"""Calibracion por canal para el modo "Espejo en Tiempo Real".

Por que hace falta
------------------
El sensor entrega el "muscle level" crudo en unidades arbitrarias (~500-1500
en reposo, con ruido de ~40 % y picos aislados enormes), y cada sensor tiene su
propia ganancia (piel, posicion, musculo): "1000" no significa lo mismo en un
canal que en otro. Ademas, si el streaming usa el parser binario de uMyo,
``dc0..dc2`` van normalizados *entre los tres canales* y un canal depende de lo
que hagan los otros dos.

Esta calibracion trabaja sobre la amplitud *cruda y limpia* de cada sensor
(``EMGDataService.latest_raw``, ver ``emg_cleaning``) y por canal fija:

- ``floor``: el percentil 90 del reposo (el ruido normal del reposo cae por
  debajo). Por debajo de esto el canal vale 0 y la mano no tiembla. Se usa un
  percentil y no "media + K * sigma": con este sensor el ruido es ~40 % del
  nivel y de cola larga, y ``K * sigma`` daba un piso mas alto que la propia
  contraccion, por lo que la calibracion casi nunca pasaba.
- ``ceil``: nivel de una contraccion fuerte (percentil 90 de la fase de
  contraccion). Ahi el canal vale 1.

y normaliza linealmente entre ambos. Es logica pura (sin hardware ni I/O) para
poder probarla aparte; el orquestador de fases vive en ``hand_mirror_service``.

Un canal se acepta solo si de verdad distingue la contraccion del reposo: al menos
``MIN_SEPARATION`` de las muestras de la contraccion deben superar el ``floor``
(y ``ceil - floor`` no puede ser minimo). Los valores se eligieron con un estudio
real de 12 movimientos (mano/antebrazo con la correa): con ellos pasan el agarre
esferico y el pulgar, y un puño flojo se rechaza a proposito, porque en esos datos
la senal del puño no se distingue del reposo (aceptarlo solo mapearia ruido).
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence


class CalibrationError(ValueError):
    """La calibracion no se pudo calcular (mensaje pensado para mostrarse al usuario)."""


# --- Parametros ---------------------------------------------------------------
MIN_SAMPLES = 10          # muestras minimas por fase para fiarse del resultado
REST_FLOOR_PERCENTILE = 0.90  # zona muerta: por debajo del P90 del reposo el canal vale 0
DEADBAND_FRAC = 0.08      # ... o esta fraccion del rango reposo->contraccion (lo que sea mayor)
CONTRACT_PERCENTILE = 0.90
MIN_SEPARATION = 0.25     # fraccion minima de la contraccion que debe superar el floor
MIN_SPAN_ABS = 20.0       # (ceil - floor) minimo, en unidades crudas del sensor
MIN_SPAN_REL = 0.15       # ... o esta fraccion del nivel de reposo (lo que sea mayor)
MAD_TO_SIGMA = 1.4826     # MAD -> desviacion estandar equivalente (distribucion normal)


def _percentile(values: Sequence[float], p: float) -> float:
    ordered = sorted(values)
    idx = int(round(p * (len(ordered) - 1)))
    return ordered[max(0, min(len(ordered) - 1, idx))]


@dataclass(frozen=True)
class ChannelCalibration:
    rest_level: float   # mediana del reposo
    rest_sigma: float   # sigma robusta (MAD) del reposo
    floor: float
    ceil: float
    separation: float = 0.0   # fraccion de la contraccion por encima del floor (0..1): calidad del canal

    def normalize(self, raw: float) -> float:
        span = self.ceil - self.floor
        if span <= 0:
            return 0.0
        return max(0.0, min(1.0, (raw - self.floor) / span))

    def to_dict(self) -> Dict[str, float]:
        return {
            "rest": round(self.rest_level, 2),
            "rest_sigma": round(self.rest_sigma, 2),
            "floor": round(self.floor, 2),
            "ceil": round(self.ceil, 2),
            "separation": round(self.separation, 2),
        }


def build_channel_calibration(
    rest_samples: Sequence[float],
    contract_samples: Sequence[float],
) -> ChannelCalibration:
    """Calcula la calibracion de UN canal a partir de sus muestras crudas."""
    if len(rest_samples) < MIN_SAMPLES or len(contract_samples) < MIN_SAMPLES:
        raise CalibrationError(
            "Llegaron muy pocas muestras del sensor; revisa la conexión e intenta de nuevo."
        )

    rest_level = statistics.median(rest_samples)
    rest_sigma = MAD_TO_SIGMA * statistics.median(abs(x - rest_level) for x in rest_samples)
    ceil = _percentile(contract_samples, CONTRACT_PERCENTILE)

    floor = max(
        _percentile(rest_samples, REST_FLOOR_PERCENTILE),
        rest_level + DEADBAND_FRAC * (ceil - rest_level),
    )
    separation = sum(1 for x in contract_samples if x > floor) / len(contract_samples)

    min_span = max(MIN_SPAN_ABS, MIN_SPAN_REL * rest_level)
    if ceil - floor < min_span or separation < MIN_SEPARATION:
        raise CalibrationError(
            f"La contracción casi no se distingue del ruido del reposo (reposo ≈ {rest_level:.0f}, "
            f"con ruido hasta ≈ {floor:.0f}; contracción ≈ {ceil:.0f}, y solo el {separation * 100:.0f} % "
            f"de ella supera el ruido; haría falta ≥ {floor + min_span:.0f} y al menos "
            f"{MIN_SEPARATION * 100:.0f} %). Revisa la posición del sensor, contrae con más fuerza "
            "y no te muevas en el reposo."
        )

    return ChannelCalibration(
        rest_level=rest_level,
        rest_sigma=rest_sigma,
        floor=floor,
        ceil=ceil,
        separation=separation,
    )


class MirrorCalibration:
    """Calibracion de los (hasta) 3 canales. Un canal ``None`` no tiene sensor."""

    def __init__(self, channels: Sequence[Optional[ChannelCalibration]]) -> None:
        self.channels: List[Optional[ChannelCalibration]] = list(channels)

    def normalize(self, raw: Sequence[float]) -> List[float]:
        """Valor 0..1 de cada canal (0 si el canal no esta calibrado)."""
        out: List[float] = []
        for i, cal in enumerate(self.channels):
            if cal is None or i >= len(raw):
                out.append(0.0)
            else:
                out.append(cal.normalize(float(raw[i])))
        return out

    def activation(self, raw: Sequence[float]) -> float:
        """Cierre 0..1: el canal mas activo (mismo criterio que sin calibrar)."""
        levels = self.normalize(raw)
        return max(levels) if levels else 0.0

    def to_list(self) -> List[Optional[Dict[str, float]]]:
        return [None if c is None else c.to_dict() for c in self.channels]
