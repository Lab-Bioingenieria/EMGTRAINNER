"""Limpieza de la senal cruda de los sensores para el control en vivo.

Contexto (medido sobre las sesiones guardadas en ``storage/sessions``):

- El ESP32 manda por serie el "muscle level" crudo de cada uMyo, una linea
  por lectura, y ``EMGDataService`` lo reenvia SIN ningun filtro ni umbral.
- Las lecturas son muy ruidosas (la desviacion robusta del reposo es ~40 % de
  su propio nivel) y traen picos aislados enormes (decenas de miles, incluso
  millones, sobre un nivel normal de ~500-1500). ~75 % de esos picos duran una
  sola lectura y ~13 % dos.
- ~64 % de las lineas consecutivas repiten exactamente el valor anterior: el
  ESP32 emite lineas mas rapido de lo que el sensor entrega lecturas nuevas.

Por eso el filtro trabaja sobre *lecturas distintas* (una linea repetida no
avanza la ventana) y combina dos etapas por canal:

1. Mediana de ``WINDOW`` lecturas: descarta picos de hasta ``(WINDOW-1)//2``
   lecturas seguidas sin recortar un aumento sostenido (una contraccion real
   sube durante muchas lecturas, asi que la mediana la sigue).
2. Suavizado exponencial (``ALPHA``) para bajar el ruido residual.

Es logica pura (sin hardware). Solo se usa para lo que mueve la mano y para
calibrar; los CSV de sesion y el grafico siguen recibiendo el dato crudo, para
no alterar los datos de entrenamiento.
"""
from __future__ import annotations

import statistics
from collections import deque
from typing import Deque, Optional, Sequence, Tuple

WINDOW = 5    # lecturas en la mediana: rechaza picos de 1-2 lecturas
ALPHA = 0.5   # 1.0 = sin suavizado; menor = mas suave pero mas retraso


class ChannelCleaner:
    def __init__(self, window: int = WINDOW, alpha: float = ALPHA) -> None:
        self._buf: Deque[float] = deque(maxlen=window)
        self._alpha = alpha
        self._last_in: Optional[float] = None
        self._out: Optional[float] = None

    def update(self, value: float) -> float:
        # Linea repetida: el sensor no entrego nada nuevo, no avanza la ventana.
        if self._out is not None and value == self._last_in:
            return self._out
        self._last_in = value
        self._buf.append(value)
        med = statistics.median(self._buf)
        if self._out is None:
            self._out = med
        else:
            self._out += self._alpha * (med - self._out)
        return self._out


class SignalCleaner:
    """Un ``ChannelCleaner`` por canal. Se crea uno nuevo al empezar cada streaming."""

    def __init__(self, n_channels: int = 3, window: int = WINDOW, alpha: float = ALPHA) -> None:
        self._channels = [ChannelCleaner(window, alpha) for _ in range(n_channels)]

    def update(self, values: Sequence[float]) -> Tuple[float, ...]:
        return tuple(c.update(float(v)) for c, v in zip(self._channels, values))
