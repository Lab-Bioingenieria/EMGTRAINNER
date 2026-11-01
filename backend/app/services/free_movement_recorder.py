"""Grabacion de datos de movimiento libre (Espejo en Tiempo Real).

Las sesiones del protocolo (``csv_service``) guardan ``nombre,edad,emg1,emg2,
emg3,labels`` con una etiqueta de gesto. Aca no hay protocolo: la persona se
mueve libremente mientras el espejo sigue su senal. Se guarda en un directorio
APARTE (``storage/free_movement``) para no mezclar estos datos con los
etiquetados que usa el entrenamiento, pero con las mismas seis primeras
columnas (y la etiqueta fija ``Libre``) para poder cargarlos con las mismas
herramientas y compararlos (``scripts/compare_sessions_vs_free.py``).

Columnas extra, utiles para la comparacion:

- ``clean1..3``: lectura ya sin picos y suavizada (``emg_cleaning``).
- ``level1..3``: nivel calibrado 0..1 de cada canal (vacio si no hay calibracion).
- ``activation``: cierre 0..1 que pide la senal (max de los ``level``).
- ``closure``: cierre realmente aplicado a la mano fisica (vacio si esta detenida).
- ``t_ms``: marca de tiempo en milisegundos.

Los ``emg1..3`` son el dato CRUDO igual que en las sesiones (en el modo texto
del ESP32 son los niveles del sensor tal cual).
"""
from __future__ import annotations

import csv
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional, TextIO

LABEL = "Libre"
FIELDS = [
    "nombre", "edad", "emg1", "emg2", "emg3", "labels",
    "clean1", "clean2", "clean3",
    "level1", "level2", "level3",
    "activation", "closure", "t_ms",
]


def safe_name(name: Optional[str]) -> str:
    """Mismo saneado que ``CSVService`` para nombres de carpeta."""
    cleaned = "".join(c for c in (name or "") if c.isalnum() or c in (" ", "_", "-")).strip()
    return cleaned or "Guest"


class FreeMovementRecorder:
    def __init__(self, storage_dir: str = "storage/free_movement") -> None:
        self.storage_dir = storage_dir
        self._file: Optional[TextIO] = None
        self._writer: Optional[csv.DictWriter] = None
        self._name = "Guest"
        self._age = ""
        self.path: Optional[str] = None      # relativo a storage_dir, con "/"
        self.rows = 0
        self._started_at = 0.0

    @property
    def is_recording(self) -> bool:
        return self._file is not None

    @property
    def seconds(self) -> float:
        return (time.monotonic() - self._started_at) if self.is_recording else 0.0

    def start(self, name: Optional[str] = None, age: Optional[str] = None) -> str:
        if self.is_recording:
            raise RuntimeError("Ya hay una grabación en curso")
        self._name = safe_name(name)
        self._age = age or ""
        target_dir = os.path.join(self.storage_dir, self._name)
        os.makedirs(target_dir, exist_ok=True)
        filename = f"libre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self._file = open(os.path.join(target_dir, filename), mode="w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=FIELDS)
        self._writer.writeheader()
        self.path = f"{self._name}/{filename}"
        self.rows = 0
        self._started_at = time.monotonic()
        return self.path

    def write(self, row: Dict[str, Any]) -> None:
        if not self._file or not self._writer:
            return
        data = {"nombre": self._name, "edad": self._age, "labels": LABEL}
        data.update(row)
        self._writer.writerow({k: ("" if data.get(k) is None else data.get(k)) for k in FIELDS})
        self.rows += 1
        if self.rows % 30 == 0:  # ~1 s de datos: no perder mucho si se corta de golpe
            self._file.flush()

    def stop(self) -> Dict[str, Any]:
        seconds = self.seconds
        if self._file:
            try:
                self._file.close()
            finally:
                self._file = None
                self._writer = None
        return {"active": False, "file": self.path, "rows": self.rows, "seconds": round(seconds, 1)}

    def summary(self) -> Dict[str, Any]:
        return {
            "active": self.is_recording,
            "file": self.path,
            "rows": self.rows,
            "seconds": round(self.seconds, 1),
        }
