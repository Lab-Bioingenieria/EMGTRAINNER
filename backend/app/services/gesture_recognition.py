"""Carga el clasificador de movimientos entrenado y lo aplica en vivo.

El modelo (medias, varianzas, prioris por clase, ver ``gesture_classifier``) lo
genera ``scripts/train_gesture_classifier.py`` a partir de las sesiones del
protocolo, y se guarda en ``storage/models/gesture_classifier.json``. Esta clase
solo lo CARGA y lo aplica sobre una ventana deslizante de muestras en vivo
(``gesture_features.RollingWindow``); no entrena nada aca.

Separado de ``hand_mirror_service`` para que ese archivo (ya grande, orquesta
el espejo, la calibracion y el estudio) no tenga que saber como se lee un
modelo ni como se arma su ventana de caracteristicas.

Importante: esto es SOLO informativo. No mueve la mano ni cambia el cierre
proporcional del espejo (eso lo decidio el equipo: primero se valida que el
clasificador acierte, antes de dejar que controle algo). Ver
``claude/clasificador-de-movimientos.md`` para los numeros de exactitud
medidos y sus limitaciones (entrena con muchas personas distintas y le cuesta
generalizar a alguien nuevo: en el estudio esta mas cerca de "supone que estas
en reposo" que de reconocer el movimiento).
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from app.services.gesture_classifier import GaussianNBClassifier
from app.services.gesture_features import RollingWindow

DEFAULT_MODEL_PATH = "storage/models/gesture_classifier.json"

# Por debajo de esto no se muestra el movimiento detectado (se ve "en reposo" o
# vacio en su lugar): con menos confianza que esto el modelo esta mas
# adivinando que reconociendo, y mostrarlo igual generaria falsa confianza.
MIN_CONFIDENCE = 0.5


class GestureRecognizer:
    def __init__(self, model_path: str = DEFAULT_MODEL_PATH) -> None:
        self.model_path = model_path
        self._clf: Optional[GaussianNBClassifier] = None
        self.meta: Dict[str, Any] = {}
        self._window = RollingWindow()
        self.reload()

    def reload(self) -> bool:
        """Vuelve a leer el modelo de disco. True si habia uno valido."""
        import json

        self._clf = None
        self.meta = {}
        try:
            with open(self.model_path, encoding="utf-8") as f:
                data = json.load(f)
            self._clf = GaussianNBClassifier.from_dict(data)
            self.meta = data.get("meta", {})
        except (OSError, ValueError, KeyError):
            pass
        return self.available

    @property
    def available(self) -> bool:
        return self._clf is not None

    def reset_window(self) -> None:
        """Vacia la ventana (por ejemplo al recalibrar: el reposo de referencia cambio)."""
        self._window = RollingWindow()

    def push(self, sample: Tuple[float, float, float]) -> None:
        self._window.push(sample)

    def predict(self, baseline: Tuple[float, float, float]) -> Optional[Dict[str, Any]]:
        """``{"label", "confidence"}`` de la ventana actual, o None si falta modelo o datos."""
        if not self.available or not self._window.ready:
            return None
        feats = self._window.features(baseline)
        label, confidence = self._clf.predict(feats)
        return {"label": label, "confidence": round(confidence, 2)}
