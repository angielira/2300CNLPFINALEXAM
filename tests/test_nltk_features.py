import ast
import pathlib

import pytest

SRC = pathlib.Path(__file__).resolve().parents[1] / "nlp" / "nltk_features.py"


def test_no_forbidden_imports():
    tree = ast.parse(SRC.read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
    assert not mods & {"spacy", "sklearn", "numpy", "pandas", "requests"}


nltk = pytest.importorskip("nltk")
from nlp import nltk_features as nf  # noqa: E402


def _need(fn, *a):
    try:
        return fn(*a)
    except LookupError:
        pytest.skip("NLTK data missing (stopwords / vader_lexicon)")


def test_tokenize_no_data_needed():
    assert nf.tokenize("Won’t PRINT, error 0x80070057!") == ["won't", "print", "error", "0x80070057"]


def test_clean_keeps_negations_and_stems():
    out = _need(nf.clean, "My printer is not working and it won't print")
    assert "not" in out and "won't" in out
    assert "my" not in out and "is" not in out
    assert "print" in out and "work" in out      # Porter: working -> work, printer -> printer
    assert "printer" in out


def test_clean_drops_stopwords():
    assert _need(nf.clean, "the and of to") == []


def test_frustrated_examples():
    r = _need(nf.frustration, "This is terrible, I hate it, everything is awful")
    assert r["frustrated"] and "vader_negative" in r["reasons"] and r["library"] == "NLTK"
    r = _need(nf.frustration, "my wifi keeps dropping!!")
    assert r["frustrated"] and "problem_phrase+exclaim" in r["reasons"]
    r = _need(nf.frustration, "The app is FROZEN again")
    assert r["frustrated"] and "problem_phrase+caps" in r["reasons"]


def test_apostrophe_free_and_crashes():
    for txt in ("my laptop WONT connect!!", "it cant print!!", "printer isnt working!!",
                "word doesnt work!!", "excel didnt work!!", "it wouldnt open!!",
                "the app crashes!!", "my phone keeps crashing!!"):
        r = _need(nf.frustration, txt)
        assert "problem_phrase+exclaim" in r["reasons"], txt
    # whole-word matching: no hit inside other words
    assert not nf._has_phrase("the wonton cantaloupe crashesque")


def test_repetition_needs_second_signal():
    r = _need(nf.frustration, "the page loads over and over")
    assert "repetition+signal" not in r["reasons"]
    r = _need(nf.frustration, "the page loads over and over!!")
    assert "repetition+signal" in r["reasons"]
    r = _need(nf.frustration, "it fails EVERY SINGLE TIME")
    assert "repetition+signal" in r["reasons"]
    r = _need(nf.frustration, "it is still not working")
    assert "repetition+signal" in r["reasons"]
    r = _need(nf.frustration, "it asks again and again")
    assert "repetition+signal" not in r["reasons"]


def test_calm_not_frustrated():
    r = _need(nf.frustration, "How do I change my wifi password?")
    assert not r["frustrated"] and r["reasons"] == []
    assert set(r) >= {"neg", "neu", "pos", "compound", "frustrated", "reasons", "library"}


def test_satisfaction_labels():
    assert _need(nf.satisfaction, "Great, very helpful, thank you!")["label"] == "positive"
    assert nf.satisfaction("This was useless and awful")["label"] == "negative"


def test_top_words_and_phrases():
    docs = [["forgot", "password"]] * 4 + [["printer", "jam"], ["wifi", "slow"], ["screen", "dark"]]
    assert nf.top_words(docs, 2)[0] == {"word": "forgot", "count": 4}
    ph = nf.top_phrases(docs, n=5, min_freq=3)
    assert ph[0]["phrase"] == "forgot password" and ph[0]["count"] == 4
    assert isinstance(ph[0]["score"], float)
