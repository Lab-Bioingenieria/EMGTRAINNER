import csv
import importlib.util
import json
import os
import sys

_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "app", "services", "calibration_study.py")
_spec = importlib.util.spec_from_file_location("calibration_study", _PATH)
cs = importlib.util.module_from_spec(_spec)
sys.modules["calibration_study"] = cs  # los dataclasses lo necesitan
_spec.loader.exec_module(cs)


def test_protocol_structure():
    steps = cs.build_protocol(["cerrar", "menique", "pulgar"], reps=3)   # el orden de la peticion no importa
    contracts = [s for s in steps if s.kind == "contract"]
    assert [s.movement for s in contracts] == ["pulgar"] * 3 + ["menique"] * 3 + ["cerrar"] * 3
    assert [s.rep for s in contracts[:3]] == [1, 2, 3]
    assert steps[0].kind == "prepare" and steps[1].kind == "rest" and steps[-1].kind == "rest"
    assert all(not s.records for s in steps if s.kind == "prepare")
    assert cs.step_label(contracts[0]) == "Pulgar"
    assert cs.step_label(contracts[-1]) == "Cerrar"
    assert cs.step_label(steps[1]) == cs.REST_LABEL


def test_protocol_validation():
    for bad in (0, 11):
        try:
            cs.build_protocol(reps=bad)
            assert False
        except cs.StudyError:
            pass
    try:
        cs.build_protocol(["nariz"])
        assert False
    except cs.StudyError:
        pass
    assert cs.normalize_movements(None) == list(cs.MOVEMENTS) and len(cs.MOVEMENTS) == 12
    assert {"Abrir", "Cerrar", "Apuntar", "Pinza", "Like", "Cilindrico", "Esferico"} <= {v[0] for v in cs.GESTURES.values()}


def test_writer_saves_csv_params_and_summary(tmp_path):
    w = cs.StudyWriter(str(tmp_path))
    path = w.start("Ana/../Perez", "30")
    rest = cs.Step("rest", None, 0, 1, "")
    idx = cs.Step("contract", "indice", 1, 1, "")
    for _ in range(10):
        w.write(rest, True, (100, 500, 300), (100.0, 500.0, 300.0), 1)
    for _ in range(10):
        w.write(idx, True, (100, 2500, 300), (100.0, 2500.0, 300.0), 2)
    w.write(idx, False, (0, 0, 0), (0.0, 0.0, 0.0), 3)   # subida: no cuenta en el resumen
    info = w.finish({"protocol": {"movements": ["indice"], "reps": 1}}, "completa")

    assert info["rows"] == 21 and ".." not in path
    folder = tmp_path / path
    rows = list(csv.DictReader(open(folder / "data.csv", newline="", encoding="utf-8")))
    assert list(rows[0].keys()) == cs.FIELDS
    assert {r["labels"] for r in rows} == {"Reposo", "Indice"}
    assert {r["group"] for r in rows} == {"", "dedo"}
    assert rows[-1]["valid"] == "0"
    params = json.load(open(folder / "params.json", encoding="utf-8"))
    assert params["status"] == "completa" and params["result"]["rows_per_label"]["Indice"] == 11
    assert params["summary"]["movements"]["indice"]["ratio_vs_rest"] == [1.0, 5.0, 1.0]

    listed = cs.list_studies(str(tmp_path))
    assert len(listed) == 1 and listed[0]["movements"] == ["indice"]


def test_empty_study_leaves_no_folder(tmp_path):
    w = cs.StudyWriter(str(tmp_path))
    path = w.start(None, None)
    info = w.finish({}, "error")
    assert info["file"] is None and not (tmp_path / path).exists()
    assert cs.list_studies(str(tmp_path)) == []
