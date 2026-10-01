"""Clasificador de movimientos: Naive Bayes Gaussiano, en Python puro.

Por que este clasificador y no una red / sklearn
--------------------------------------------------
El backend no tiene hoy ninguna dependencia de machine learning (se reviso
``requirements.txt``: ni numpy ni scikit-learn). Sumar una para esto obligaria
a instalarla a mano en cada equipo que corra el backend, y el volumen de datos
(miles de ventanas, 12 caracteristicas) no lo necesita. Naive Bayes Gaussiano:

- Se entrena en una pasada (media y varianza por clase y caracteristica: nada
  de gradientes ni hiperparametros que ajustar).
- Es barato de evaluar en vivo (unas pocas sumas y logaritmos por prediccion),
  lo que importa porque corre en el mismo bucle que ya mueve la mano.
- Serializa a JSON plano (medias, varianzas, prioris): se puede inspeccionar o
  versionar sin pickles ni formatos binarios.

Asume caracteristicas condicionalmente independientes dada la clase (de ahi
"naive"): con 12 caracteristicas y unas pocas miles de muestras por clase es
una aproximacion razonable, aunque un modelo mas expresivo (SVM, red pequena)
probablemente clasifique mejor si mas adelante se justifica la dependencia.

Varianza compartida (``shared_variance=True``, por defecto)
-------------------------------------------------------------
Con datos de EMG de muchas personas mezcladas, la varianza DENTRO de cada
clase no es solo ruido: es tambien cuanto varia esa clase entre personas
distintas. Si una clase tiene pocas ventanas o resulta mas homogenea entre
sesiones (por azar, no porque sea mas facil de distinguir), su varianza
estimada queda chica y el termino ``1/sqrt(var)`` de la Gaussiana la vuelve
artificialmente "puntuda": absorbe casi todas las predicciones aunque su
media no sea la mas cercana. Esto se probo con las sesiones reales del
protocolo: "cerrar" tenia la menor varianza de las 8 clases y el modelo le
asignaba la mayoria de las ventanas de prueba, con una exactitud por debajo
de adivinar al azar. Compartir una unica varianza por caracteristica (el
promedio ponderado por tamano de cada clase, equivalente a un LDA Gaussiano
con covarianza diagonal) evita ese sesgo: todas las clases quedan con la
misma "anchura" y compiten solo por la distancia de la media.
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

# Var minima (en unidades de caracteristica al cuadrado) para que una clase no quede
# con varianza ~0 en alguna caracteristica (por ejemplo si todas sus ventanas de
# entrenamiento fueron casi identicas) y termine dando probabilidades absurdas.
MIN_VARIANCE = 1e-4


class GaussianNBClassifier:
    """Naive Bayes Gaussiano multiclase sobre vectores de caracteristicas."""

    def __init__(self) -> None:
        self.classes_: List[str] = []
        self.feature_names: List[str] = []
        self._priors: Dict[str, float] = {}
        self._means: Dict[str, List[float]] = {}
        self._vars: Dict[str, List[float]] = {}

    @property
    def is_fitted(self) -> bool:
        return bool(self.classes_)

    def fit(
        self,
        X: Sequence[Sequence[float]],
        y: Sequence[str],
        feature_names: Sequence[str],
        shared_variance: bool = True,
    ) -> None:
        if len(X) != len(y):
            raise ValueError("X e y deben tener la misma longitud")
        if not X:
            raise ValueError("No hay datos para entrenar")
        n_features = len(X[0])
        self.feature_names = list(feature_names)
        if len(self.feature_names) != n_features:
            raise ValueError("feature_names no coincide con las columnas de X")

        by_class: Dict[str, List[Sequence[float]]] = {}
        for row, label in zip(X, y):
            by_class.setdefault(label, []).append(row)

        self.classes_ = sorted(by_class)
        total = len(y)
        self._priors, self._means = {}, {}
        per_class_vars: Dict[str, List[float]] = {}
        for label, rows in by_class.items():
            self._priors[label] = len(rows) / total
            means: List[float] = []
            variances: List[float] = []
            for j in range(n_features):
                col = [r[j] for r in rows]
                m = sum(col) / len(col)
                v = sum((x - m) ** 2 for x in col) / len(col) if len(col) > 1 else 0.0
                means.append(m)
                variances.append(v)
            self._means[label] = means
            per_class_vars[label] = variances

        if shared_variance:
            # Varianza compartida entre clases (ver docstring del modulo): promedio de
            # cada caracteristica ponderado por cuantas ventanas aporto cada clase.
            pooled: List[float] = []
            for j in range(n_features):
                pooled.append(
                    sum(per_class_vars[label][j] * len(by_class[label]) for label in self.classes_) / total
                )
            pooled = [max(v, MIN_VARIANCE) for v in pooled]
            self._vars = {label: list(pooled) for label in self.classes_}
        else:
            self._vars = {
                label: [max(v, MIN_VARIANCE) for v in vs] for label, vs in per_class_vars.items()
            }

    def _log_likelihood(self, x: Sequence[float], label: str) -> float:
        means, variances = self._means[label], self._vars[label]
        log_p = math.log(self._priors[label])
        for xi, m, v in zip(x, means, variances):
            log_p += -0.5 * math.log(2 * math.pi * v) - ((xi - m) ** 2) / (2 * v)
        return log_p

    def predict_proba(self, x: Sequence[float]) -> Dict[str, float]:
        if not self.is_fitted:
            raise RuntimeError("El clasificador no esta entrenado")
        logs = {label: self._log_likelihood(x, label) for label in self.classes_}
        top = max(logs.values())
        exps = {label: math.exp(v - top) for label, v in logs.items()}  # estabilidad numerica
        total = sum(exps.values()) or 1.0
        return {label: v / total for label, v in exps.items()}

    def predict(self, x: Sequence[float]) -> Tuple[str, float]:
        proba = self.predict_proba(x)
        label = max(proba, key=proba.get)
        return label, proba[label]

    # ------------------------------------------------------------------ (de)serializacion
    def to_dict(self) -> Dict:
        return {
            "schema_version": 1,
            "classes": self.classes_,
            "feature_names": self.feature_names,
            "priors": self._priors,
            "means": self._means,
            "variances": self._vars,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GaussianNBClassifier":
        clf = cls()
        clf.classes_ = list(data["classes"])
        clf.feature_names = list(data["feature_names"])
        clf._priors = dict(data["priors"])
        clf._means = {k: list(v) for k, v in data["means"].items()}
        clf._vars = {k: list(v) for k, v in data["variances"].items()}
        return clf
