"""build.py evaluation code, checked with stand-ins for NLTK and spaCy (runs without either)."""
import pathlib
import sys
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.build import spacy_metrics, vader_metrics  # noqa: E402


def _fake_nf(flagged: set):
    def frustration(text):
        hit = text in flagged
        return {"frustrated": hit, "reasons": ["vader_negative"] if hit else []}
    return SimpleNamespace(frustration=frustration, FRUSTRATION_THRESHOLD=-0.4)


def test_vader_metrics_counts_and_test_split():
    rows = [
        {"text": "a", "frustrated": "1", "split": "train"},   # TP
        {"text": "b", "frustrated": "1", "split": "test"},    # FN (test)
        {"text": "c", "frustrated": "0", "split": "test"},    # FP (test)
        {"text": "d", "frustrated": "1", "split": "test"},    # TP (test)
        {"text": "e", "frustrated": "0", "split": "train"},   # TN
    ]
    m = vader_metrics(rows, _fake_nf({"a", "c", "d"}))
    assert m["library"] == "NLTK" and m["n"] == 5 and m["n_frustrated"] == 3
    assert m["precision"] == round(2 / 3, 4) and m["recall"] == round(2 / 3, 4)
    assert m["test"] == {"n": 3, "n_frustrated": 2, "precision": 0.5, "recall": 0.5, "f1": 0.5}
    assert m["false_negatives"] == ["b"] and m["false_positives"] == ["c"]
    assert m["true_positive_reasons"] == {"vader_negative": 2}
    assert vader_metrics(rows, None) is None


def test_spacy_metrics_entities_and_problems():
    gold = [
        {"text": "My HP printer won't print", "entities": [{"text": "HP printer", "label": "DEVICE"}],
         "problems": [{"thing": "printer", "problem": "not print"}]},
        {"text": "wifi on my phone is slow", "entities": [{"text": "phone", "label": "DEVICE"}],
         "problems": [{"thing": "wifi", "problem": "slow"}]},
        {"text": "How do I add a printer?", "entities": [], "problems": []},
    ]
    out = [
        {"entities": [{"text": "HP  Printer", "label": "DEVICE"}, {"text": "HP", "label": "ORG"}],
         "problems": [{"thing": "Printer", "problem": "not print"}]},
        {"entities": [{"text": "wifi", "label": "DEVICE"}, {"text": "phone", "label": "DEVICE"}],
         "problems": [{"thing": "wifi", "problem": "be slow"}]},
        {"entities": [{"text": "printer", "label": "DEVICE"}], "problems": []},
    ]
    sf = SimpleNamespace(analyze=lambda texts, nlp: out[:len(texts)])
    m = spacy_metrics(gold, sf, None)
    assert m["entity_counts"] == {"tp": 2, "fp": 2, "fn": 0}       # ORG ignored, case/space-insensitive
    assert m["entity_precision"] == 0.5 and m["entity_recall"] == 1.0
    assert m["problem_n"] == 2 and m["problem_accuracy"] == 0.5 and m["problem_thing_accuracy"] == 1.0
    assert [e["text"] for e in m["problem_errors"]] == ["wifi on my phone is slow"]
    assert spacy_metrics(gold, None, None) is None
