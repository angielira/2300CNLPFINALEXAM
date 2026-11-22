"""Tests for nlp/spacy_features.py.

Part 1 needs only the standard library (pattern file, export). Part 2 needs spaCy and
en_core_web_sm and is skipped when either is missing.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PATTERNS = ROOT / "nlp" / "patterns" / "it_entities.jsonl"
HINTS = ROOT / "nlp" / "patterns" / "category_hints.json"
LABELS = {"DEVICE", "APP", "OS", "ERROR_CODE"}
CATEGORY_IDS = {"printer", "email", "wifi", "passwords", "slow", "phone_apps", "files", "video_calls"}


# ----------------------------------------------------------------- stdlib only
def _lines():
    return [ln for ln in PATTERNS.read_text(encoding="utf-8").splitlines() if ln.strip()]


def test_every_jsonl_line_parses_and_has_label_and_pattern():
    lines = _lines()
    assert len(lines) > 100
    for n, ln in enumerate(lines, 1):
        obj = json.loads(ln)
        assert obj.get("label") in LABELS, f"line {n}"
        pat = obj.get("pattern")
        assert isinstance(pat, (str, list)) and pat, f"line {n}"
        assert obj.get("id"), f"line {n}"
        if isinstance(pat, list):
            assert all(isinstance(t, dict) and t for t in pat), f"line {n}"


def test_every_label_is_present_and_core_terms_exist():
    objs = [json.loads(ln) for ln in _lines()]
    assert {o["label"] for o in objs} == LABELS
    ids = {o["id"] for o in objs}
    for needed in ("printer", "router", "laptop", "webcam", "iphone", "android", "outlook", "gmail", "zoom",
                   "teams", "chrome", "windows", "macos", "onedrive", "google_drive", "wifi", "bluetooth",
                   "hex_error", "http_error"):
        assert needed in ids, needed


def test_category_hints_are_valid_and_cover_every_category():
    hints = json.loads(HINTS.read_text(encoding="utf-8"))
    ids = {json.loads(ln)["id"] for ln in _lines()}
    assert set(hints) <= ids
    assert set(hints.values()) == CATEGORY_IDS


def test_export_patterns_writes_contract(tmp_path):
    pytest.importorskip("nlp.common")
    from nlp import spacy_features as sf

    out = tmp_path / "entity_patterns.json"
    payload = sf.export_patterns(str(out))
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["library"] == "spaCy" and data["schema_version"] == 1 and data["generated_at"]
    assert data["labels"] == ["DEVICE", "APP", "OS", "ERROR_CODE"]
    assert data["regex"] and data["regex"][0]["label"] == "ERROR_CODE"
    assert isinstance(data["skipped_patterns"], int)
    assert payload["items"] == data["items"]
    by_id = {i["id"]: i for i in data["items"]}
    printer = by_id["printer"]
    assert printer["label"] == "DEVICE" and printer["category_hint"] == "printer"
    assert {"printer", "printers", "hp printer", "canon printer"} <= set(printer["phrases"])
    assert by_id["outlook"]["category_hint"] == "email"
    assert "microsoft outlook" in by_id["outlook"]["phrases"]
    assert {"windows", "windows 11", "windows 10"} <= set(by_id["windows"]["phrases"])
    assert by_id["wifi"]["phrases"].count("wi-fi") == 1
    for item in data["items"]:
        assert item["label"] in LABELS
        assert item["category_hint"] is None or item["category_hint"] in CATEGORY_IDS
        assert all(p == p.lower() and p == p.strip() and p for p in item["phrases"])
    # regex-only error ids are covered by JS_REGEX, not exported as phrases
    assert "hex_error" not in by_id
    assert len(out.read_bytes()) < 1_000_000


def test_phrase_expansion_handles_optional_tokens_and_plurals():
    from nlp import spacy_features as sf

    phrases, status = sf._pattern_phrases([{"LOWER": {"IN": ["hp", "canon"]}, "OP": "?"}, {"LEMMA": "printer"}])
    assert status == "ok"
    assert set(phrases) == {"printer", "printers", "hp printer", "hp printers", "canon printer", "canon printers"}
    assert sf._pattern_phrases([{"TEXT": {"REGEX": "^0x"}}])[1] == "regex"
    assert sf._pattern_phrases([{"POS": "NOUN"}])[1] == "skipped"
    assert sf._pattern_phrases("Google Drive") == (["google drive"], "ok")


# ----------------------------------------------------------------- needs spaCy
@pytest.fixture(scope="module")
def nlp():
    pytest.importorskip("spacy")
    from nlp import spacy_features as sf

    try:
        return sf.build_nlp()
    except OSError:
        pytest.skip("en_core_web_sm is not installed")


@pytest.fixture(scope="module")
def sf():
    pytest.importorskip("spacy")
    from nlp import spacy_features

    return spacy_features


def _ents(sf, nlp, text):
    return {(e["text"].lower(), e["label"]) for e in sf.entities(nlp(text))}


def test_ruler_sits_before_ner(nlp):
    names = nlp.pipe_names
    assert "entity_ruler" in names and names.index("entity_ruler") < names.index("ner")


def test_entities_devices_apps_os_codes(sf, nlp):
    got = _ents(sf, nlp, "My HP printer shows error 0x80070005 in Outlook on Windows 11")
    assert ("hp printer", "DEVICE") in got
    assert ("0x80070005", "ERROR_CODE") in got
    assert ("outlook", "APP") in got
    assert ("windows 11", "OS") in got


def test_entities_are_case_insensitive_and_plural(sf, nlp):
    got = _ents(sf, nlp, "my PRINTERS and ROUTER are not talking to GMAIL")
    assert ("printers", "DEVICE") in got
    assert ("router", "DEVICE") in got
    assert ("gmail", "APP") in got


def test_entity_id_groups_variants(sf, nlp):
    ids = {e["id"] for e in sf.entities(nlp("Printers and my Canon printer"))}
    assert "printer" in ids


def test_http_error_code(sf, nlp):
    got = _ents(sf, nlp, "The website shows error 404")
    assert any(label == "ERROR_CODE" and "404" in text for text, label in got)


def test_entity_dict_has_contract_keys(sf, nlp):
    text = "Zoom on my iPhone"
    for e in sf.entities(nlp(text)):
        assert set(e) == {"text", "label", "start_char", "end_char", "id"}
        assert text[e["start_char"]:e["end_char"]] == e["text"]


def test_problem_negation(sf, nlp):
    pairs = sf.problems(nlp("My printer won't print"))
    assert {"thing": "printer", "problem": "not print", "negated": True} in pairs


def test_problem_not_working(sf, nlp):
    pairs = sf.problems(nlp("My laptop is not working"))
    assert any(p["thing"] == "laptop" and p["negated"] and p["problem"].endswith("work") for p in pairs)


def test_problem_adjective(sf, nlp):
    pairs = sf.problems(nlp("The printer is broken"))
    assert {"thing": "printer", "problem": "broken", "negated": False} in pairs


def test_problem_keeps_dropping(sf, nlp):
    pairs = sf.problems(nlp("My wifi keeps dropping"))
    assert {"thing": "wifi", "problem": "keep drop", "negated": False} in pairs


def test_problem_without_verb(sf, nlp):
    pairs = sf.problems(nlp("printer broken"))
    assert any(p["thing"] == "printer" and p["problem"] == "broken" for p in pairs)


def test_no_problem_in_plain_how_to(sf, nlp):
    assert sf.problems(nlp("How do I add a new printer to my Windows 11 laptop?")) == []


def test_good_adjective_is_not_a_problem(sf, nlp):
    assert sf.problems(nlp("The wifi is fine on my phone")) == []


def test_pronoun_subject_uses_nearest_entity(sf, nlp):
    pairs = sf.problems(nlp("My Outlook will not start and I can't open it"))
    assert any(p["thing"] == "outlook" and p["negated"] and p["problem"] == "not open" for p in pairs)


def test_quoted_error_text(sf, nlp):
    pairs = sf.problems(nlp('Gmail says "couldn\'t send" every time I attach a photo'))
    assert any(p["thing"] == "gmail" and p["negated"] and p["problem"].endswith("send") for p in pairs)


def test_new_problem_verbs(sf, nlp):
    pairs = sf.problems(nlp("The Instagram app closes on its own and my phone battery drains fast"))
    problems = {p["problem"] for p in pairs}
    assert "close" in problems and "drain" in problems


def test_close_as_user_action_is_not_a_problem(sf, nlp):
    assert sf.problems(nlp("How do I close the Zoom app?")) == []


def test_wont_without_apostrophe_is_negated(sf, nlp):
    pairs = sf.problems(nlp("my hp printer wont print"))
    assert any(p["thing"] == "printer" and p["negated"] and p["problem"] == "not print" for p in pairs)


def test_negation_words_cover_split_wont(sf):
    assert "nt" in sf.NEGATION_WORDS and {"close", "drain", "spin", "wipe"} <= sf.PROBLEM_VERBS


def test_tags(sf, nlp):
    result = sf.tags(nlp("My printers keep jamming and the ink runs out on my Windows laptop"))
    assert result == sorted(set(result))
    assert "printer" in result and "ink" in result and "laptop" in result
    assert all(len(t) >= 3 and t == t.lower() for t in result)
    assert "my" not in result


def test_analyze_matches_single_calls(sf, nlp):
    texts = ["My printer won't print", "Zoom has no sound"]
    batch = sf.analyze(texts, nlp, batch_size=2)
    assert len(batch) == 2
    assert batch[0]["entities"] == sf.entities(nlp(texts[0]))
    assert batch[0]["problems"] == sf.problems(nlp(texts[0]))
    assert batch[1]["tags"] == sf.tags(nlp(texts[1]))


def test_gold_file_entities_found(sf, nlp):
    gold = ROOT / "data" / "spacy_gold.jsonl"
    if not gold.exists():
        pytest.skip("data/spacy_gold.jsonl missing")
    rows = [json.loads(ln) for ln in gold.read_text(encoding="utf-8").splitlines() if ln.strip()]
    hit = total = 0
    for row in rows:
        found = {e["text"].lower() for e in sf.entities(nlp(row["text"]))}
        for e in row["entities"]:
            total += 1
            hit += e["text"].lower() in found
    assert total and hit / total >= 0.6, f"recall {hit}/{total}"
