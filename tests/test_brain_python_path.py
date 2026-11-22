"""Simulates what site/js/brain-worker.js runs in Pyodide (Python side only).

The Python glue is extracted from the worker file itself, so this tests the real code path.
Files are copied the way the worker writes them: site/py/* -> /py, listed in nltk_manifest.json.
"""
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
WORKER = SITE / "js" / "brain-worker.js"


def _glue() -> str:
    src = WORKER.read_text()
    body = src.split("// PY_GLUE_START", 1)[1].split("// PY_GLUE_END", 1)[0]
    parts = re.search(r"var PY_GLUE = (\[.*?\])\.join", body, re.S).group(1)
    return "\n".join(json.loads(parts))


@pytest.fixture()
def brain(tmp_path, monkeypatch):
    pytest.importorskip("numpy")
    manifest = json.loads((SITE / "data" / "nltk_manifest.json").read_text())
    py_root = tmp_path / "py"
    for f in manifest["python_files"]:
        dest = py_root / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SITE / manifest["python_base_url"] / f, dest)
    data_root = tmp_path / "nltk_data"
    for f in manifest["items"]:
        dest = data_root / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SITE / manifest["base_url"] / f, dest)
    model_text = (SITE / "data" / "model.json").read_text()
    glue = _glue().replace("'/py'", repr(str(py_root))).replace("'/nltk_data'", repr(str(data_root)))
    for m in [k for k in sys.modules if k == "nlp" or k.startswith("nlp.")]:
        monkeypatch.delitem(sys.modules, m)
    monkeypatch.setattr(sys, "path", list(sys.path))
    sys.path[:] = [p for p in sys.path if p != str(ROOT)]   # only the temp copy may provide "nlp"
    ns = {"_model_json": model_text}
    exec(glue, ns)
    yield ns, json.loads(model_text)
    for m in [k for k in sys.modules if k == "nlp" or k.startswith("nlp.")]:
        sys.modules.pop(m, None)


def test_worker_contract_shape(brain):
    ns, model = brain
    r = json.loads(ns["helpmate_analyze"]("my printer is not printing"))
    assert r["category"] in model["classes"]
    assert 0.0 <= r["confidence"] <= 1.0
    assert set(r["probabilities"]) == set(model["classes"])
    assert abs(sum(r["probabilities"].values()) - 1.0) < 1e-6
    assert isinstance(r["unsure"], bool)
    assert set(r["mood"]) == {"compound", "frustrated", "reasons"}


def test_unsure_when_no_known_words(brain):
    ns, _ = brain
    assert json.loads(ns["helpmate_analyze"]("zzqx qwvv"))["unsure"] is True
    assert json.loads(ns["helpmate_analyze"](""))["unsure"] is True


def test_unsure_matches_threshold(brain):
    ns, model = brain
    r = json.loads(ns["helpmate_analyze"]("wifi keeps dropping"))
    if r["known_terms"]:
        assert r["unsure"] == (r["confidence"] < model["min_confidence"])


def test_simple_tokenizer_needs_no_nltk_data(brain):
    ns, model = brain
    if model["tokenizer"] != "simple_v1":
        pytest.skip("shipped model uses nltk_clean_v1")
    # prediction must work even without nltk; mood is simply absent then
    r = json.loads(ns["helpmate_analyze"]("my printer will not print"))
    assert r["tokenizer"] == "simple_v1"
    if not ns["_NLTK_OK"]:
        assert r["mood_ok"] is False and r["mood"]["frustrated"] is False


def test_mood_with_nltk(brain):
    pytest.importorskip("nltk")
    ns, _ = brain
    r = json.loads(ns["helpmate_analyze"]("This is TERRIBLE!! My printer is broken and nothing works"))
    if not r["mood_ok"]:
        pytest.skip("VADER lexicon not in site/nltk_data (build ran without NLTK data)")
    assert r["mood"]["frustrated"] is True
    assert r["mood"]["reasons"]
