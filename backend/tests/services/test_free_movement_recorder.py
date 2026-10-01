import csv
import importlib.util
import os

_HERE = os.path.dirname(__file__)
_PATH = os.path.join(_HERE, "..", "..", "app", "services", "free_movement_recorder.py")
_spec = importlib.util.spec_from_file_location("free_movement_recorder", _PATH)
fmr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fmr)


def test_records_session_format_plus_extras(tmp_path):
    rec = fmr.FreeMovementRecorder(str(tmp_path))
    path = rec.start("Ana/../Perez", "30")
    rec.write({"emg1": 1, "emg2": 2, "emg3": 3, "clean1": 1.5, "level1": 0.4, "activation": 0.4})
    rec.write({"emg1": 4, "emg2": 5, "emg3": 6})
    info = rec.stop()

    assert info["rows"] == 2 and info["active"] is False
    assert ".." not in path and "/" in path
    with open(tmp_path / path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert list(rows[0].keys()) == fmr.FIELDS
    assert rows[0]["labels"] == "Libre" and rows[0]["edad"] == "30"
    assert rows[1]["level1"] == "" and rows[1]["activation"] == ""


def test_default_name_and_no_double_start(tmp_path):
    rec = fmr.FreeMovementRecorder(str(tmp_path))
    assert rec.start(None).startswith("Guest/")
    try:
        rec.start("x")
        assert False
    except RuntimeError:
        pass
    rec.write({"emg1": 1})   # sin error
    rec.stop()
    rec.write({"emg1": 2})   # detenido: se ignora
    assert rec.rows == 1
