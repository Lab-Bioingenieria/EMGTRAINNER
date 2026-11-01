"""Estudio de calibracion: protocolo guiado + almacenamiento de cada sesion.

Objetivo: juntar, sesion tras sesion, datos etiquetados de la senal de los
sensores mientras la persona mueve UN dedo a la vez y hace gestos completos de
la mano (cerrar, abrir, apuntar, pinza...), para entrenar despues un modelo que
detecte cada dedo y cada gesto. Cada sesion se guarda en su propia carpeta:

    storage/calibration_studies/<nombre>/<YYYYMMDD_HHMMSS>/
        data.csv     senal cruda + limpia, etiquetada por dedo / fase / repeticion
        params.json  participante, protocolo, parametros de la senal, resumen

``data.csv`` empieza con las mismas columnas que las sesiones del protocolo
(``nombre,edad,emg1,emg2,emg3,labels``) para poder cargarlo con las mismas
herramientas; ``labels`` es el movimiento (dedo o gesto, con los mismos nombres
que las sesiones: Cerrar, Abrir, Apuntar, Pinza, Like, Cilindrico, Esferico)
mientras se contrae y ``Reposo`` el resto del tiempo. Columnas extra:

- ``clean1..3``: lectura sin picos y suavizada (``emg_cleaning``).
- ``movement``: clave del movimiento del bloque (tambien durante su relajacion).
- ``group``: ``dedo`` | ``gesto`` (vacio en el reposo inicial/final).
- ``phase``: ``rest`` | ``contract`` | ``relax``.
- ``rep``: numero de repeticion (0 en el reposo inicial/final).
- ``valid``: 0 durante el primer tramo de cada bloque (subida / bajada de la
  fuerza, sin etiqueta fiable), 1 el resto. Para entrenar conviene filtrar ``valid == 1``.
- ``t_ms``: marca de tiempo en milisegundos.

Es logica pura (sin hardware ni asyncio): el servicio del espejo la conduce.
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, TextIO, Tuple

REST_LABEL = "Reposo"

# clave -> (etiqueta de entrenamiento, nombre en pantalla, instruccion al contraer).
# Etiquetas sin tildes para no depender de la codificacion del CSV; los gestos usan los
# mismos nombres que las sesiones del protocolo para poder juntarlos con esos datos.
FINGERS: Dict[str, Tuple[str, str, str]] = {
    "pulgar": ("Pulgar", "pulgar", "Mueve SOLO el pulgar (flexiónalo)"),
    "indice": ("Indice", "índice", "Mueve SOLO el índice (flexiónalo)"),
    "medio": ("Medio", "dedo medio", "Mueve SOLO el dedo medio (flexiónalo)"),
    "anular": ("Anular", "anular", "Mueve SOLO el anular (flexiónalo)"),
    "menique": ("Menique", "meñique", "Mueve SOLO el meñique (flexiónalo)"),
}
GESTURES: Dict[str, Tuple[str, str, str]] = {
    "cerrar": ("Cerrar", "cerrar la mano", "Cierra el puño con fuerza"),
    "abrir": ("Abrir", "abrir la mano", "Abre la mano al máximo, extendiendo todos los dedos"),
    "apuntar": ("Apuntar", "apuntar", "Apunta con el índice extendido y el resto de dedos cerrados"),
    "pinza": ("Pinza", "pinza", "Haz la pinza: junta la punta del pulgar con la del índice"),
    "like": ("Like", "like (pulgar arriba)", "Cierra el puño y deja el pulgar arriba"),
    "cilindrico": ("Cilindrico", "agarre cilíndrico", "Agarre cilíndrico: como sujetar un vaso"),
    "esferico": ("Esferico", "agarre esférico", "Agarre esférico: como sujetar una pelota"),
}
GROUP_FINGER, GROUP_GESTURE = "dedo", "gesto"
# Todos los movimientos, en el orden del protocolo: primero los dedos, luego los gestos.
MOVEMENTS: Dict[str, Tuple[str, str, str, str]] = {
    **{k: (*v, GROUP_FINGER) for k, v in FINGERS.items()},
    **{k: (*v, GROUP_GESTURE) for k, v in GESTURES.items()},
}

FIELDS = [
    "nombre", "edad", "emg1", "emg2", "emg3", "labels",
    "clean1", "clean2", "clean3",
    "movement", "group", "phase", "rep", "valid", "t_ms",
]

DEFAULT_REPS = 5
MIN_REPS, MAX_REPS = 1, 10

INITIAL_PREP_S = 3.0
INITIAL_REST_S = 10.0
MOVEMENT_PREP_S = 4.0
CONTRACT_S = 3.0
RELAX_S = 3.0
FINAL_REST_S = 5.0
CONTRACT_SETTLE_S = 1.0   # se marca valid=0 el inicio de la contraccion (sube la fuerza)
RELAX_SETTLE_S = 1.0      # ... y el de la relajacion (baja la fuerza)
REST_SETTLE_S = 0.5


@dataclass(frozen=True)
class Step:
    kind: str                 # prepare | rest | contract | relax
    movement: Optional[str]   # clave de MOVEMENTS, o None en el reposo
    rep: int
    seconds: float
    message: str
    settle: float = 0.0       # segundos iniciales con valid=0 (solo pasos que graban)

    @property
    def records(self) -> bool:
        return self.kind != "prepare"


class StudyError(RuntimeError):
    pass


def safe_name(name: Optional[str]) -> str:
    """Mismo saneado que ``CSVService`` para nombres de carpeta."""
    cleaned = "".join(c for c in (name or "") if c.isalnum() or c in (" ", "_", "-")).strip()
    return cleaned or "Guest"


def normalize_movements(movements: Optional[Sequence[str]]) -> List[str]:
    if not movements:
        return list(MOVEMENTS)
    keys = []
    for m in movements:
        if m not in MOVEMENTS:
            raise StudyError(f"Movimiento desconocido: {m}")
        if m not in keys:
            keys.append(m)
    # se conserva el orden natural del protocolo, no el de la peticion
    return [k for k in MOVEMENTS if k in keys]


def build_protocol(movements: Optional[Sequence[str]] = None, reps: int = DEFAULT_REPS) -> List[Step]:
    if not MIN_REPS <= reps <= MAX_REPS:
        raise StudyError(f"Las repeticiones deben estar entre {MIN_REPS} y {MAX_REPS}")
    keys = normalize_movements(movements)
    steps: List[Step] = [
        Step("prepare", None, 0, INITIAL_PREP_S,
             "Prepárate: relaja por completo el brazo y déjalo quieto."),
        Step("rest", None, 0, INITIAL_REST_S,
             "Reposo: mantén el brazo relajado, sin moverte.", REST_SETTLE_S),
    ]
    for key in keys:
        _label, name, instruction, group = MOVEMENTS[key]
        if group == GROUP_FINGER:
            prep = f"Prepárate: vas a mover SOLO el {name}. Mantén el resto de la mano relajada."
        else:
            prep = f"Prepárate: vas a hacer el gesto «{name}» y a mantenerlo."
        steps.append(Step("prepare", key, 0, MOVEMENT_PREP_S, prep))
        for rep in range(1, reps + 1):
            steps.append(Step("contract", key, rep, CONTRACT_S, f"¡{instruction} y mantén!", CONTRACT_SETTLE_S))
            steps.append(Step("relax", key, rep, RELAX_S, "Relaja la mano por completo.", RELAX_SETTLE_S))
    steps.append(Step(
        "rest", None, 0, FINAL_REST_S,
        "Reposo final: relaja el brazo y no te muevas.", REST_SETTLE_S,
    ))
    return steps


def total_seconds(steps: Sequence[Step]) -> float:
    return sum(s.seconds for s in steps)


def step_label(step: Step) -> str:
    """Etiqueta de entrenamiento: el movimiento mientras se contrae, ``Reposo`` en lo demas."""
    if step.kind == "contract" and step.movement:
        return MOVEMENTS[step.movement][0]
    return REST_LABEL


class StudyWriter:
    """Escribe una sesion del estudio (``data.csv`` + ``params.json``)."""

    def __init__(self, storage_dir: str = "storage/calibration_studies") -> None:
        self.storage_dir = storage_dir
        self._file: Optional[TextIO] = None
        self._writer: Optional[csv.DictWriter] = None
        self._dir: Optional[str] = None
        self._name = "Guest"
        self._age = ""
        self.path: Optional[str] = None       # "<nombre>/<fecha>" relativo a storage_dir
        self.rows = 0
        self._started_at = 0.0
        self.rows_per_label: Dict[str, int] = {}
        # niveles limpios validos para el resumen: {(fase, dedo): [[c1..], [c2..], [c3..]]}
        self._levels: Dict[str, List[List[float]]] = {}

    @property
    def is_open(self) -> bool:
        return self._file is not None

    def start(self, name: Optional[str], age: Optional[str]) -> str:
        if self.is_open:
            raise StudyError("Ya hay un estudio en curso")
        self._name = safe_name(name)
        self._age = age or ""
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._dir = os.path.join(self.storage_dir, self._name, stamp)
        os.makedirs(self._dir, exist_ok=True)
        self._file = open(os.path.join(self._dir, "data.csv"), mode="w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=FIELDS)
        self._writer.writeheader()
        self.path = f"{self._name}/{stamp}"
        self.rows = 0
        self.rows_per_label = {}
        self._levels = {}
        self._started_at = time.monotonic()
        return self.path

    def write(self, step: Step, valid: bool, emg: Sequence[Any], clean: Sequence[float], t_ms: int) -> None:
        if not self._file or not self._writer:
            return
        label = step_label(step)
        row = {
            "nombre": self._name, "edad": self._age,
            "emg1": emg[0], "emg2": emg[1], "emg3": emg[2],
            "labels": label,
            "clean1": round(clean[0], 2), "clean2": round(clean[1], 2), "clean3": round(clean[2], 2),
            "movement": step.movement or "",
            "group": MOVEMENTS[step.movement][3] if step.movement else "",
            "phase": step.kind, "rep": step.rep,
            "valid": int(valid), "t_ms": t_ms,
        }
        self._writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in FIELDS})
        self.rows += 1
        self.rows_per_label[label] = self.rows_per_label.get(label, 0) + 1
        if valid:
            key = f"{step.kind}:{step.movement or ''}"
            cols = self._levels.setdefault(key, [[], [], []])
            for i in range(3):
                cols[i].append(float(clean[i]))
        if self.rows % 30 == 0:  # ~1 s de datos: no perder mucho si se corta de golpe
            self._file.flush()

    def seconds(self) -> float:
        return (time.monotonic() - self._started_at) if self.is_open else 0.0

    def summary(self) -> Dict[str, Any]:
        """Por movimiento y canal: mediana con contraccion / mediana en reposo (>1 = el canal responde).

        El reposo de referencia junta todo lo que se grabo en reposo y relajacion
        de esta sesion. Sirve para ver de un vistazo que sensores distinguen cada movimiento.
        """
        rest_cols: List[List[float]] = [[], [], []]
        for key, cols in self._levels.items():
            if key.startswith(("rest:", "relax:")):
                for i in range(3):
                    rest_cols[i].extend(cols[i])
        baseline = [statistics.median(c) if c else None for c in rest_cols]
        out: Dict[str, Any] = {"baseline_rest": [round(b, 1) if b is not None else None for b in baseline]}
        movements: Dict[str, Any] = {}
        for key, cols in self._levels.items():
            phase, _, movement = key.partition(":")
            if phase != "contract" or not movement or not cols[0]:
                continue
            ratios = []
            for i in range(3):
                base = baseline[i]
                med = statistics.median(cols[i])
                ratios.append(round(med / base, 2) if base else None)
            movements[movement] = {"n": len(cols[0]), "ratio_vs_rest": ratios}
        out["movements"] = movements
        return out

    def finish(self, params: Dict[str, Any], status: str) -> Dict[str, Any]:
        """Cierra el CSV y escribe ``params.json``. Sin filas, borra la carpeta vacia."""
        seconds = round(self.seconds(), 1)
        if self._file:
            try:
                self._file.close()
            finally:
                self._file = None
                self._writer = None
        info = {"file": self.path, "rows": self.rows, "seconds": seconds, "status": status}
        if self._dir is None:
            return info
        if self.rows == 0:
            shutil.rmtree(self._dir, ignore_errors=True)
            info["file"] = None
            return info
        payload = {
            "schema_version": 1,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "status": status,   # completa | cancelada | error
            "participant": {"nombre": self._name, "edad": self._age},
            **params,
            "result": {
                "rows": self.rows,
                "seconds": seconds,
                "rows_per_label": self.rows_per_label,
                "approx_hz": round(self.rows / seconds, 1) if seconds else None,
            },
            "summary": self.summary(),
        }
        with open(os.path.join(self._dir, "params.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return info


def list_studies(storage_dir: str = "storage/calibration_studies", limit: int = 30) -> List[Dict[str, Any]]:
    """Ultimas sesiones guardadas (las mas recientes primero), leidas de sus ``params.json``."""
    found: List[Dict[str, Any]] = []
    if not os.path.isdir(storage_dir):
        return found
    for name in os.listdir(storage_dir):
        person_dir = os.path.join(storage_dir, name)
        if not os.path.isdir(person_dir):
            continue
        for stamp in os.listdir(person_dir):
            pj = os.path.join(person_dir, stamp, "params.json")
            if not os.path.isfile(pj):
                continue
            try:
                with open(pj, encoding="utf-8") as f:
                    p = json.load(f)
            except (OSError, ValueError):
                continue
            proto = p.get("protocol", {})
            found.append({
                "id": f"{name}/{stamp}",
                "participant": name,
                "created_at": p.get("created_at"),
                "status": p.get("status"),
                "rows": p.get("result", {}).get("rows", 0),
                "seconds": p.get("result", {}).get("seconds", 0),
                "movements": proto.get("movements", []),
                "reps": proto.get("reps"),
            })
    found.sort(key=lambda s: (s.get("created_at") or "", s["id"]), reverse=True)
    return found[:limit]
