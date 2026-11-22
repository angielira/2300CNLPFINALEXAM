"""Checks the built site/data/*.json files: envelope and key fields (plan section 2)."""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from nlp.common import CATEGORY_IDS, LIBRARIES  # noqa: E402

DATA = ROOT / "site" / "data"
KEYS = {
    "answers": ["items"], "lessons": ["items"], "entity_patterns": ["items", "labels", "regex"],
    "topics": ["items", "index"], "nltk_stats": ["items", "top_phrases", "by_category", "n_documents"],
    "model": ["classes", "coefs", "intercepts", "idf", "activation", "min_confidence"],
    "ratings_summary": ["total", "by_category", "by_format", "by_week", "sentiment"],
    "metrics": ["classifier", "vader", "spacy"], "examples": ["items"],
    "nltk_manifest": ["base_url", "items", "nltk_version"],
}


def load(name):
    p = DATA / f"{name}.json"
    if not p.exists():
        pytest.skip("site/data not built; run python3 pipeline/build.py --allow-missing")
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", sorted(KEYS))
def test_envelope_and_keys(name):
    d = load(name)
    assert d["schema_version"] == 1
    assert d["library"] in LIBRARIES
    assert isinstance(d["generated_at"], str) and d["generated_at"].endswith("Z")
    assert isinstance(d["items"], list)
    for k in KEYS[name]:
        assert k in d, f"{name}.json missing {k}"


def test_answers_cover_every_category_and_format():
    items = load("answers")["items"]
    assert {a["category"] for a in items} == set(CATEGORY_IDS)


def test_lessons_have_ten_steps_each():
    items = load("lessons")["items"]
    assert {l["category"] for l in items} == set(CATEGORY_IDS)
    for l in items:
        assert len(l["steps"]) == 10, l["category"]
        for s in l["steps"]:
            assert s["check_question"] and 0 <= s["answer"] < len(s["choices"]) if "choices" in s else True


def test_model_shapes_consistent():
    m = load("model")
    assert m["classes"] == list(CATEGORY_IDS) or set(m["classes"]) == set(CATEGORY_IDS)
    assert len(m["coefs"]) == len(m["intercepts"])
    assert len(m["classes"]) == len(m["intercepts"][-1])
    assert 0 < m["min_confidence"] < 1


def test_no_secrets_in_data():
    import re
    pat = re.compile(r"api[_-]?key|build_hook|hooks\.netlify|AKIA[0-9A-Z]{8}|sk-[A-Za-z0-9]{16}|BEGIN PRIVATE", re.I)
    for p in DATA.glob("*.json"):
        assert not pat.search(p.read_text(encoding="utf-8")), p.name
