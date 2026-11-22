"""Runs the local build (--allow-missing) into a temp folder and checks every output file."""
import json
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nlp.common import CATEGORY_IDS, LIBRARIES  # noqa: E402

FILES = ["answers", "lessons", "entity_patterns", "topics", "nltk_stats", "model",
         "ratings_summary", "metrics", "examples", "nltk_manifest"]


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    if os.environ.get("NETLIFY") == "true":
        pytest.skip("--allow-missing is refused on Netlify")
    from pipeline import build
    d = tmp_path_factory.mktemp("site")
    assert build.main(["--out", str(d), "--allow-missing"]) == 0
    return d


def load(out, name):
    return json.loads((out / "data" / f"{name}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", FILES)
def test_envelope_and_size(out, name):
    p = out / "data" / f"{name}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["schema_version"] == 1 and d["library"] in LIBRARIES and d["generated_at"].endswith("Z")
    assert isinstance(d["items"], list)
    assert p.stat().st_size < (2_000_000 if name == "model" else 1_000_000)


def test_answers_lessons_order(out):
    assert [a["category"] for a in load(out, "answers")["items"]] == CATEGORY_IDS
    assert all(sorted(a["format_rank"]) == sorted(["see_it", "hear_it", "try_it", "read_it"])
               for a in load(out, "answers")["items"])
    assert [a["category"] for a in load(out, "lessons")["items"]] == CATEGORY_IDS


def test_topics_index(out):
    t = load(out, "topics")
    assert set(t["index"]) == set(CATEGORY_IDS)
    ids = {i["id"] for i in t["items"]}
    assert all(x in ids for v in t["index"].values() for x in v)


def test_model_and_metrics(out):
    m = load(out, "model")
    assert m["tokenizer"] == "simple_v1" or m["tokenizer"] == "nltk_clean_v1"
    assert len(m["vocabulary"]) == len(m["idf"]) == len(m["coefs"][0])
    c = load(out, "metrics")["classifier"]
    assert c["confusion_matrix"]["labels"] == CATEGORY_IDS
    assert load(out, "metrics")["items"] == []


def test_no_comment_text_in_ratings(out):
    s = json.dumps(load(out, "ratings_summary"))
    assert '"comment"' not in s and '"question"' not in s


def test_browser_files_and_manifest(out):
    man = load(out, "nltk_manifest")
    for rel in man["python_files"]:
        assert (out / "py" / rel).exists()
    for rel in man["items"]:
        assert (out / "nltk_data" / rel).exists()
    assert (out / "assets/brand/helpmate-mark.svg").exists()
    assert (ROOT / "reports/classifier.md").exists()


def test_allow_missing_refused_on_netlify(monkeypatch, tmp_path):
    from pipeline import build
    monkeypatch.setenv("NETLIFY", "true")
    assert build.main(["--out", str(tmp_path), "--allow-missing"]) == 1


def test_missing_nltk_fails_without_flag(tmp_path):
    pytest.importorskip("sklearn")
    try:
        import nltk  # noqa: F401
        pytest.skip("nltk installed")
    except ImportError:
        pass
    from pipeline import build
    assert build.main(["--out", str(tmp_path)]) == 1
