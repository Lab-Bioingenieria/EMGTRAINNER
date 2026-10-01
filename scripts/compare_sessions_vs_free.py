#!/usr/bin/env python3
"""Compara las sesiones del protocolo (con gesto) contra grabaciones de movimiento libre.

Uso (desde la raiz del repo):
    python scripts/compare_sessions_vs_free.py
    python scripts/compare_sessions_vs_free.py --sessions-dir backend/storage/sessions \
        --free-dir backend/storage/free_movement --out informe.md

Solo biblioteca estandar. Las sesiones traen ``nombre,edad,emg1..3,labels``; las
grabaciones libres (``FreeMovementRecorder``) traen ademas ``clean*``, ``level*``,
``activation``... y la etiqueta ``Libre``.

Como cada grabacion tiene su propia escala (colocacion, ganancia), los niveles se
expresan RELATIVOS al reposo de esa grabacion: reposo ~ mediana del 30 % mas bajo
de las lecturas de cada canal. Asi 1.0 = nivel de reposo, 3.0 = triple, etc.
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import statistics
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

CH = ("emg1", "emg2", "emg3")
SPIKE_FACTOR = 10.0   # una lectura > 10x la mediana del canal cuenta como pico


def _num(v: str) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def pct(vals: List[float], q: float) -> float:
    if not vals:
        return float("nan")
    s = sorted(vals)
    k = (len(s) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def rest_level(vals: List[float]) -> float:
    """Proxy robusto del reposo: mediana del 30 % mas bajo (sin ceros)."""
    v = sorted(x for x in vals if x > 0)
    if not v:
        return 1.0
    return statistics.median(v[: max(1, int(len(v) * 0.3))]) or 1.0


def quality(rows: List[dict]) -> Dict[str, float]:
    out: Dict[str, float] = {"rows": len(rows)}
    spikes = tot = rep = 0
    cvs = []
    for c in CH:
        vals = [x for x in (_num(r.get(c, "")) for r in rows) if x is not None]
        if len(vals) < 2:
            continue
        med = statistics.median(vals) or 1.0
        spikes += sum(1 for x in vals if x > SPIKE_FACTOR * med)
        tot += len(vals)
        rep += sum(1 for a, b in zip(vals, vals[1:]) if a == b)
        low = sorted(vals)[: max(2, int(len(vals) * 0.3))]
        m = statistics.mean(low)
        if m:
            cvs.append(statistics.pstdev(low) / m)
    out["spike_pct"] = 100 * spikes / tot if tot else float("nan")
    out["repeat_pct"] = 100 * rep / tot if tot else float("nan")
    out["rest_cv"] = statistics.mean(cvs) if cvs else float("nan")
    return out


def relative_levels(rows: List[dict], source: str) -> Dict[str, Dict[str, List[float]]]:
    """{label: {canal: [nivel relativo al reposo]}} usando la columna cruda (o limpia)."""
    cols = {c: [_num(r.get(c, "")) for r in rows] for c in CH}
    rests = {c: rest_level([x for x in v if x is not None]) for c, v in cols.items()}
    res: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    for i, r in enumerate(rows):
        label = (r.get("labels") or "?").strip()
        for c in CH:
            x = cols[c][i]
            if x is not None:
                res[label][c].append(x / rests[c])
    return res


def fmt(x: float, nd: int = 1) -> str:
    return "-" if x != x else f"{x:.{nd}f}"


def collect(dirpath: str) -> List[Tuple[str, List[dict]]]:
    files = sorted(glob.glob(os.path.join(dirpath, "**", "*.csv"), recursive=True))
    return [(os.path.relpath(f, dirpath), load_csv(f)) for f in files]


def build_report(sessions_dir: str, free_dir: str) -> str:
    sess = collect(sessions_dir)
    free = collect(free_dir)
    L: List[str] = [f"# Sesiones vs movimiento libre ({datetime.now():%Y-%m-%d %H:%M})", ""]
    L.append(f"- Sesiones del protocolo: {len(sess)} archivo(s)")
    L.append(f"- Grabaciones libres: {len(free)} archivo(s)")
    L.append("")
    if not free:
        L += ["> Todavía no hay grabaciones libres. Graba desde «Espejo en Tiempo Real» "
              "(tarjeta «Grabar movimiento libre») y vuelve a ejecutar este script.", ""]

    # --- 1. Calidad de datos ---
    L += ["## 1. Calidad de la señal cruda", "",
          "| Grupo | Archivos | Lecturas | Picos (>10x mediana) | Líneas repetidas | Ruido en reposo (CV) |",
          "|---|---|---|---|---|---|"]
    for name, data in (("Sesiones", sess), ("Libre", free)):
        qs = [quality(rows) for _, rows in data if rows]
        if not qs:
            continue
        L.append(
            f"| {name} | {len(qs)} | {int(sum(q['rows'] for q in qs))} | "
            f"{fmt(statistics.mean(q['spike_pct'] for q in qs), 2)} % | "
            f"{fmt(statistics.mean(q['repeat_pct'] for q in qs), 0)} % | "
            f"{fmt(statistics.mean(q['rest_cv'] for q in qs), 2)} |")
    L.append("")

    # --- 2. Nivel relativo al reposo por etiqueta ---
    pooled: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    for group in (sess, free):
        for _, rows in group:
            if not rows:
                continue
            for label, chans in relative_levels(rows, "raw").items():
                for c, v in chans.items():
                    pooled[label][c].extend(v)
    L += ["## 2. Nivel relativo al reposo por etiqueta (P50 / P90 por canal)", "",
          "Cada grabación se divide por su propio reposo (1.0 = reposo).", "",
          "| Etiqueta | Lecturas | Sensor 1 | Sensor 2 | Sensor 3 |", "|---|---|---|---|---|"]
    order = sorted(pooled, key=lambda k: (k == "Libre", k))
    for label in order:
        n = len(pooled[label]["emg1"])
        cells = [f"{fmt(pct(pooled[label][c], .5))} / {fmt(pct(pooled[label][c], .9))}" for c in CH]
        L.append(f"| {label} | {n} | " + " | ".join(cells) + " |")
    L.append("")

    # --- 3. Activacion calibrada en libre ---
    acts: List[float] = []
    for _, rows in free:
        acts += [a for a in (_num(r.get("activation", "")) for r in rows) if a is not None]
    L.append("## 3. Activación calibrada en movimiento libre")
    L.append("")
    if not acts:
        L += ["Sin datos calibrados (las grabaciones libres se hicieron sin calibrar).", ""]
    else:
        bins = [(0, .1), (.1, .3), (.3, .6), (.6, .9), (.9, 1.01)]
        L += [f"{len(acts)} lecturas calibradas.", "", "| Rango | % del tiempo |", "|---|---|"]
        for lo, hi in bins:
            share = 100 * sum(1 for a in acts if lo <= a < hi) / len(acts)
            L.append(f"| {lo:.1f}–{min(hi, 1):.1f} | {share:.0f} % |")
        L.append("")
        L.append(f"Mediana {fmt(statistics.median(acts), 2)}, P90 {fmt(pct(acts, .9), 2)}. "
                 "Si casi todo cae en 0–0.1 la mano apenas se moverá; si casi todo está en "
                 "0.9–1.0 la calibración quedó demasiado sensible.")
        L.append("")

    L += ["## Cómo leerlo", "",
          "- Si «Libre» tiene P90 parecido al de los gestos, el movimiento libre trae "
          "suficiente señal para que el espejo responda.",
          "- Si el ruido en reposo (CV) o los picos son mucho mayores en Libre que en las "
          "sesiones, revisa la colocación de la correa antes de tocar umbrales.",
          "- Un canal con P90 ≈ 1.0 en todas las etiquetas no aporta información: "
          "conviene ignorarlo en la calibración.", ""]
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sessions-dir", default="backend/storage/sessions")
    ap.add_argument("--free-dir", default="backend/storage/free_movement")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    report = build_report(a.sessions_dir, a.free_dir)
    out = a.out or os.path.join("backend", "storage", "reports", f"comparacion_{datetime.now():%Y%m%d_%H%M%S}.md")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\nInforme guardado en {out}")


if __name__ == "__main__":
    main()
