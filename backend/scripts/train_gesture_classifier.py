#!/usr/bin/env python3
"""Entrena el clasificador de movimientos con TODAS las sesiones etiquetadas del
centro de entrenamiento: las del protocolo (CE-xx) y las del Estudio de
calibracion por dedo del Espejo. Es un solo modelo: todo lo que se graba en el
centro de entrenamiento alimenta el mismo clasificador.

Uso (desde la raiz del repo, con el backend en el PYTHONPATH):
    python backend/scripts/train_gesture_classifier.py
    python backend/scripts/train_gesture_classifier.py \
        --sessions-dir backend/storage/sessions backend/storage/calibration_studies \
        --out-model backend/storage/models/gesture_classifier.json

Que hace
--------
1. Lee cada CSV de dos fuentes (por defecto ambas a la vez, ver ``--sessions-dir``):
   - ``storage/sessions/<participante>/*.csv``: las sesiones del protocolo (solo
     gestos completos de la mano + reposo).
   - ``storage/calibration_studies/<participante>/<fecha>/data.csv``: el Estudio
     de calibracion por dedo que se graba desde la pantalla del Espejo (cada dedo
     por separado ademas de los gestos + reposo). Se diseño a proposito con las
     MISMAS columnas y los MISMOS nombres de gesto que las sesiones del protocolo
     (``nombre,edad,emg1,emg2,emg3,labels``, columnas extra que se ignoran aca)
     para poder juntarlas sin transformacion. Como agrega dedos sueltos, el
     modelo entrenado con ambas fuentes puede reconocer mas clases que
     entrenando solo con el protocolo (ver ``LABEL_TO_MOVEMENT``: los nombres de
     dedo no estan ahi porque pasan sin cambios, ya vienen en la clave correcta).
2. Reproduce esa senal cruda por el MISMO limpiador que usa el espejo en vivo
   (``emg_cleaning.SignalCleaner``), para que el modelo entrene con datos
   procesados igual que como los vera en produccion.
3. Calcula el reposo de la sesion (mediana de las filas etiquetadas "Rest") y
   trocea cada bloque de gesto en ventanas solapadas de
   ``gesture_features.WINDOW_SIZE`` filas, descartando el arranque de cada
   bloque (``SETTLE_ROWS``: ahi la fuerza esta subiendo o bajando).
4. Separa los PARTICIPANTES (no las filas) en entrenamiento y prueba, para que
   la exactitud reportada sea sobre gente que el modelo no vio entrenar: una
   sesion no debe filtrarse entre train y test. El nombre de participante es el
   mismo aunque venga de las dos fuentes (misma carpeta), asi que a alguien que
   grabo protocolo Y estudio no se lo cuenta como dos personas distintas ni se
   filtra entre train/test.
5. Entrena un Naive Bayes Gaussiano (``gesture_classifier``) y evalua:
   exactitud global, por clase (precision/recall/F1) y matriz de confusion.
6. Reentrena con TODOS los participantes (para desplegar) y guarda el modelo
   en JSON. Escribe tambien un informe en Markdown con las metricas.

Es un punto de partida, no un resultado final: agregar mas sesiones o mejorar
la colocacion de los sensores cambia estos numeros. Vuelve a correr el script
cuando haya sesiones nuevas (de cualquiera de las dos fuentes).
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import os
import random
import sys
from collections import Counter
from datetime import datetime
from typing import Dict, List, Sequence, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVICES = os.path.join(_HERE, "..", "app", "services")


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_SERVICES, filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


emg_cleaning = _load("emg_cleaning", "emg_cleaning.py")
gesture_features = _load("gesture_features", "gesture_features.py")
gesture_classifier = _load("gesture_classifier", "gesture_classifier.py")

# Las sesiones vienen en latin-1 (se verifico con `file`: "CSV ISO-8859 text") y con
# nombres de gesto sin normalizar (acentos, "Rest" en ingles). Se mapean a las MISMAS
# claves que ya usa el estudio de calibracion (`calibration_study.GESTURES`), asi el
# modelo entrenado aca y los datos del estudio hablan el mismo idioma.
LABEL_TO_MOVEMENT = {
    "rest": "reposo", "reposo": "reposo",
    "abrir": "abrir", "cerrar": "cerrar", "apuntar": "apuntar", "pinza": "pinza", "like": "like",
    "cilindrico": "cilindrico", "cilíndrico": "cilindrico",
    "esferico": "esferico", "esférico": "esferico", "esf�rico": "esferico",
}
REST_KEY = "reposo"

# Algunas sesiones tienen un bloque de reposo enorme (miles de filas: la persona se
# quedo conectada sin moverse) frente a bloques tipicos de ~130-170 filas. Sin limite,
# ESA sesion por si sola domina la clase "reposo" del dataset entero. Se limita cuantas
# ventanas aporta un mismo bloque continuo (submuestreadas parejo a lo largo del bloque).
MAX_WINDOWS_PER_BLOCK = 40


def _normalize_label(raw: str) -> str:
    key = raw.strip().lower()
    return LABEL_TO_MOVEMENT.get(key, key)


def _read_session_csv(path: str) -> List[Dict[str, str]]:
    import csv
    for encoding in ("latin-1", "utf-8"):
        try:
            with open(path, encoding=encoding) as f:
                rows = list(csv.DictReader(f))
            if all("�" not in (r.get("labels") or "") for r in rows):
                return rows
        except (UnicodeDecodeError, csv.Error):
            continue
    with open(path, encoding="latin-1") as f:
        return list(csv.DictReader(f))


def _session_windows(rows: List[Dict[str, str]]) -> List[Tuple[List[float], str]]:
    """[(caracteristicas, movimiento)] de UNA sesion, limpiando y ventaneando por bloque."""
    cleaner = emg_cleaning.SignalCleaner()
    clean: List[Tuple[float, float, float]] = []
    movement: List[str] = []
    for r in rows:
        try:
            raw = (float(r["emg1"]), float(r["emg2"]), float(r["emg3"]))
        except (KeyError, ValueError):
            continue
        clean.append(cleaner.update(raw))
        movement.append(_normalize_label(r.get("labels", "")))

    rest_samples = [clean[i] for i, m in enumerate(movement) if m == REST_KEY]
    if len(rest_samples) < gesture_features.WINDOW_SIZE:
        return []  # sesion sin reposo suficiente para tener una referencia: se descarta
    baseline = tuple(
        sorted(rest_samples[i][c] for i in range(len(rest_samples)))[len(rest_samples) // 2]
        for c in range(3)
    )

    out: List[Tuple[List[float], str]] = []
    n = len(clean)
    start = 0
    while start < n:
        end = start
        while end < n and movement[end] == movement[start]:
            end += 1
        label = movement[start]
        block = clean[start + gesture_features.SETTLE_ROWS: end]
        w = gesture_features.WINDOW_SIZE
        offsets = list(range(0, max(0, len(block) - w + 1), gesture_features.STEP))
        if len(offsets) > MAX_WINDOWS_PER_BLOCK:
            # Submuestreo parejo a lo largo del bloque, no solo el principio.
            keep = {round(i * (len(offsets) - 1) / (MAX_WINDOWS_PER_BLOCK - 1)) for i in range(MAX_WINDOWS_PER_BLOCK)}
            offsets = [o for i, o in enumerate(offsets) if i in keep]
        for i in offsets:
            out.append((gesture_features.window_features(block[i:i + w], baseline), label))
        start = end
    return out


def _session_paths(sessions_dir: str) -> List[str]:
    return sorted(glob.glob(os.path.join(sessions_dir, "**", "*.csv"), recursive=True))


def build_dataset(sessions_dirs: Sequence[str]) -> Tuple[List[List[float]], List[str], List[str]]:
    """X, y, participante (mismo orden) de todas las sesiones encontradas en TODOS los
    directorios dados (protocolo + estudio de calibracion, normalmente): se recorren en
    el orden recibido y se juntan en un solo dataset. El nombre de carpeta de primer nivel
    es el participante en las dos fuentes (``<participante>/*.csv`` y
    ``<participante>/<fecha>/data.csv``), asi que el mismo nombre en dos directorios se
    trata como la misma persona (no se filtra entre train/test, ver ``split_by_participant``).
    """
    X: List[List[float]] = []
    y: List[str] = []
    groups: List[str] = []
    for sessions_dir in sessions_dirs:
        for path in _session_paths(sessions_dir):
            participant = os.path.relpath(path, sessions_dir).split(os.sep)[0]
            rows = _read_session_csv(path)
            for feats, label in _session_windows(rows):
                X.append(feats)
                y.append(label)
                groups.append(participant)
    return X, y, groups


def split_by_participant(
    groups: Sequence[str], test_fraction: float, seed: int
) -> Tuple[List[int], List[int]]:
    participants = sorted(set(groups))
    rng = random.Random(seed)
    rng.shuffle(participants)
    n_test = max(1, round(len(participants) * test_fraction))
    test_participants = set(participants[:n_test])
    train_idx = [i for i, g in enumerate(groups) if g not in test_participants]
    test_idx = [i for i, g in enumerate(groups) if g in test_participants]
    return train_idx, test_idx


def evaluate(clf, X_test: List[List[float]], y_test: List[str]) -> Dict:
    classes = sorted(set(y_test) | set(clf.classes_))
    confusion: Dict[str, Counter] = {c: Counter() for c in classes}
    correct = 0
    for x, true in zip(X_test, y_test):
        pred, _ = clf.predict(x)
        confusion[true][pred] += 1
        correct += int(pred == true)
    accuracy = correct / len(y_test) if y_test else 0.0

    per_class = {}
    for c in classes:
        tp = confusion[c][c]
        support = sum(confusion[c].values())
        predicted_as_c = sum(confusion[t][c] for t in classes)
        precision = tp / predicted_as_c if predicted_as_c else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_class[c] = {"support": support, "precision": round(precision, 2), "recall": round(recall, 2), "f1": round(f1, 2)}

    return {
        "accuracy": round(accuracy, 3),
        "n_test_windows": len(y_test),
        "per_class": per_class,
        "confusion": {t: dict(confusion[t]) for t in classes},
        "classes": classes,
    }


def format_report(meta: Dict, metrics: Dict) -> str:
    L = [f"# Clasificador de movimientos ({meta['created_at']})", ""]
    L += [
        f"- Sesiones usadas: {meta['n_sessions']} ({meta['n_participants']} participantes)",
        f"- Ventanas: {meta['n_windows']} (entrenamiento: {meta['n_train']}, prueba: {meta['n_test']})",
        f"- Participantes de prueba (no vistos al entrenar): {', '.join(meta['test_participants']) or '-'}",
        f"- Ventana: {meta['window_size']} lecturas, avance {meta['step']}, se descartan las primeras {meta['settle_rows']} de cada bloque",
        "",
        f"## Exactitud global (sobre participantes no vistos): {metrics['accuracy'] * 100:.0f} %",
        "",
        "| Movimiento | Ventanas | Precision | Recall | F1 |",
        "|---|---|---|---|---|",
    ]
    for c in metrics["classes"]:
        m = metrics["per_class"][c]
        L.append(f"| {c} | {m['support']} | {m['precision']} | {m['recall']} | {m['f1']} |")
    L += ["", "## Matriz de confusion (filas = real, columnas = predicho)", "",
          "| real \\ predicho | " + " | ".join(metrics["classes"]) + " |",
          "|---|" + "---|" * len(metrics["classes"])]
    for real in metrics["classes"]:
        row = metrics["confusion"].get(real, {})
        L.append(f"| {real} | " + " | ".join(str(row.get(c, 0)) for c in metrics["classes"]) + " |")
    L += ["", "## Como leerlo", "",
          "- Recall bajo en un movimiento: el modelo no lo reconoce cuando de verdad pasa "
          "(se confunde con otro, mira su fila).",
          "- Precision baja: el modelo dice ese movimiento de mas (mira su columna, que otros "
          "movimientos se le estan colando).",
          "- Esto se mide con participantes que el modelo NUNCA vio entrenar: es la exactitud "
          "esperable con una persona nueva, no con la persona de las sesiones de entrenamiento.", ""]
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--sessions-dir", nargs="+", metavar="DIR",
        default=[
            os.path.join(_HERE, "..", "storage", "sessions"),
            os.path.join(_HERE, "..", "storage", "calibration_studies"),
        ],
        help="uno o mas directorios con sesiones etiquetadas (por defecto: sessions + calibration_studies)",
    )
    ap.add_argument("--out-model", default=os.path.join(_HERE, "..", "storage", "models", "gesture_classifier.json"))
    ap.add_argument("--out-report", default=None)
    ap.add_argument("--test-fraction", type=float, default=0.2, help="fraccion de PARTICIPANTES para prueba")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    print(f"Leyendo sesiones de {', '.join(args.sessions_dir)} ...")
    X, y, groups = build_dataset(args.sessions_dir)
    if not X:
        print("No se encontraron ventanas de entrenamiento (revisa --sessions-dir).")
        return
    participants = sorted(set(groups))
    print(f"{len(X)} ventanas de {len(participants)} participantes. Clases: {Counter(y)}")

    train_idx, test_idx = split_by_participant(groups, args.test_fraction, args.seed)
    X_train, y_train = [X[i] for i in train_idx], [y[i] for i in train_idx]
    X_test, y_test = [X[i] for i in test_idx], [y[i] for i in test_idx]
    test_participants = sorted({groups[i] for i in test_idx})

    print(f"Entrenando con {len(X_train)} ventanas, evaluando con {len(X_test)} de {test_participants} ...")
    clf = gesture_classifier.GaussianNBClassifier()
    clf.fit(X_train, y_train, gesture_features.FEATURE_NAMES)
    metrics = evaluate(clf, X_test, y_test)
    print(f"Exactitud (participantes no vistos): {metrics['accuracy'] * 100:.0f} %")

    # Modelo final: reentrenar con TODO (train + test) para desplegar.
    final_clf = gesture_classifier.GaussianNBClassifier()
    final_clf.fit(X, y, gesture_features.FEATURE_NAMES)

    meta = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "n_sessions": sum(len(_session_paths(d)) for d in args.sessions_dir),
        "n_participants": len(participants),
        "n_windows": len(X),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "test_participants": test_participants,
        "window_size": gesture_features.WINDOW_SIZE,
        "step": gesture_features.STEP,
        "settle_rows": gesture_features.SETTLE_ROWS,
    }

    os.makedirs(os.path.dirname(args.out_model), exist_ok=True)
    with open(args.out_model, "w", encoding="utf-8") as f:
        json.dump({**final_clf.to_dict(), "meta": meta, "held_out_metrics": metrics}, f, ensure_ascii=False, indent=2)
    print(f"Modelo guardado en {args.out_model}")

    report = format_report(meta, metrics)
    out_report = args.out_report or os.path.join(
        _HERE, "..", "storage", "reports", f"clasificador_{datetime.now():%Y%m%d_%H%M%S}.md"
    )
    os.makedirs(os.path.dirname(out_report), exist_ok=True)
    with open(out_report, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Informe guardado en {out_report}")
    print()
    print(report)


if __name__ == "__main__":
    main()
