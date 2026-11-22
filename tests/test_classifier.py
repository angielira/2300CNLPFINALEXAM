import csv
import json
import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

pytest.importorskip("sklearn")
from nlp import classifier  # noqa: E402
from nlp.common import CATEGORY_IDS  # noqa: E402

TOK = "simple_v1"


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    rows = list(csv.DictReader(open(ROOT / "data" / "seed_questions.csv", encoding="utf-8")))
    tr = [r for r in rows if r["split"] == "train"]
    te = [r for r in rows if r["split"] == "test"]
    vec, clf, m = classifier.train([r["text"] for r in tr], [r["category"] for r in tr],
                                   [r["text"] for r in te], [r["category"] for r in te], tokenizer=TOK)
    path = tmp_path_factory.mktemp("m") / "model.json"
    classifier.export_json(vec, clf, str(path), tokenizer=TOK,
                           extra={"trained_on": {"n_train": len(tr), "n_feedback": 0}})
    return vec, clf, m, path, [r["text"] for r in te]


def test_parity_with_sklearn(trained):
    vec, clf, _, path, test_texts = trained
    model = json.loads(path.read_text(encoding="utf-8"))
    proba = clf.predict_proba(vec.transform(test_texts))
    for text, p in zip(test_texts, proba):
        out = classifier.predict_numpy(model, text)
        got = np.array([out["probabilities"][c] for c in clf.classes_])
        assert np.allclose(got, p, atol=1e-4), text
        assert out["category"] == clf.classes_[int(p.argmax())]
        assert out["library"] == "Neural network"


def test_export_schema(trained):
    _, clf, m, path, _ = trained
    model = json.loads(path.read_text(encoding="utf-8"))
    assert model["library"] == "Neural network" and model["schema_version"] == 1
    assert isinstance(model["vocabulary"], list)
    n = len(model["vocabulary"])
    assert len(model["idf"]) == n
    assert len(model["coefs"][0]) == n and len(model["coefs"][0][0]) == 64
    assert len(model["coefs"][1]) == 64 and len(model["coefs"][1][0]) == 8
    assert [len(b) for b in model["intercepts"]] == [64, 8]
    assert model["classes"] == sorted(CATEGORY_IDS)
    assert model["tokenizer"] == TOK and model["ngram_range"] == list(classifier.NGRAM_RANGE)
    assert model["activation"] == "relu" and model["out_activation"] == "softmax"
    assert model["min_confidence"] == 0.45 and model["items"] == []
    assert m["confusion_matrix"]["labels"] == CATEGORY_IDS
    assert set(m["per_class"]) == set(CATEGORY_IDS)


def test_size_cap(trained):
    assert trained[3].stat().st_size < 2_000_000


def test_unsure_when_no_known_terms(trained):
    model = json.loads(trained[3].read_text(encoding="utf-8"))
    out = classifier.predict_numpy(model, "zzzz qqqq")
    assert out["known_terms"] == 0 and out["unsure"] is True


def test_module_top_level_imports_are_light():
    src = (ROOT / "nlp" / "classifier.py").read_text(encoding="utf-8")
    top = [l for l in src.splitlines() if l.startswith(("import ", "from "))]
    assert not any("sklearn" in l or "nltk" in l or "common" in l for l in top)


def test_train_default_split_is_stratified():
    rows = list(csv.DictReader(open(ROOT / "data" / "seed_questions.csv", encoding="utf-8")))
    _, _, m = classifier.train([r["text"] for r in rows], [r["category"] for r in rows], tokenizer=TOK)
    assert m["n_test"] == round(len(rows) * 0.2)
    assert all(v["support"] >= 1 for v in m["per_class"].values())
