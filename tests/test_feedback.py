import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from pipeline import feedback as fb
from nlp.common import CATEGORY_IDS, FORMATS


def row(stars=5, cat="printer", fmt="see_it", comment="", question="why wont my printer print", **kw):
    d = {"id": "x", "created_at": "2026-11-18T10:00:00Z", "stars": stars, "comment": comment,
         "question": question, "category": cat, "format": fmt}
    d.update(kw)
    return d


def test_empty_feedback(monkeypatch):
    s = fb.summarize([])
    assert s["total"] == 0 and s["items"] == [] and s["by_week"] == [] and s["flagged"] == []
    assert s["format_rank"]["printer"] == FORMATS
    assert set(s["format_rank"]) == set(CATEGORY_IDS)
    assert s["sentiment"] == {"positive": None, "neutral": None, "negative": None}
    assert fb.training_rows([]) == []


def test_no_token_no_sample(monkeypatch):
    for k in ("NETLIFY_API_TOKEN", "SITE_ID", "HELPMATE_FEEDBACK_FILE"):
        monkeypatch.delenv(k, raising=False)
    assert fb.load_feedback(sample_fallback=False) == []


def test_sample_file_fallback(monkeypatch):
    for k in ("NETLIFY_API_TOKEN", "SITE_ID", "HELPMATE_FEEDBACK_FILE"):
        monkeypatch.delenv(k, raising=False)
    rows = fb.load_feedback()
    assert rows and all(r.get("sample") for r in rows)
    assert all(1 <= r["stars"] <= 5 and r["category"] in CATEGORY_IDS and r["format"] in FORMATS for r in rows)
    s = fb.summarize(rows)
    assert s["total"] == len(rows)
    assert json.dumps(s)  # serializable
    assert fb.training_rows(rows) == []  # fake rows never train the model
    assert fb.training_rows(rows, include_sample=True)


def test_invalid_rows_dropped(tmp_path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"items": [row(stars=9), row(stars="abc"), row(cat="nope"), row(fmt="nope"),
                                       {"id": "n", "data": row(stars="4")}, row()]}))
    rows = fb.load_feedback(path=str(p))
    assert len(rows) == 2 and rows[0]["stars"] == 4


def test_pii_masked(tmp_path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"items": [row(comment="mail me at jo.smith@example.com or call +1 (555) 123-4567",
                                           question="my printer at 555-123-4567 is off, jo@x.org")]}))
    r = fb.load_feedback(path=str(p))[0]
    blob = r["comment"] + r["question"]
    assert "@" not in blob and "555" not in blob
    assert "[email removed]" in r["comment"] and "[phone removed]" in r["comment"]


def test_scores_rank_flags():
    rows = [row(5, fmt="try_it")] * 4 + [row(1, fmt="read_it")] * 3 + [row(3, cat="wifi", fmt="see_it")]
    s = fb.summarize(rows)
    by = {(i["category"], i["format"]): i for i in s["items"]}
    assert by[("printer", "try_it")]["score"] > 0.6 > by[("printer", "read_it")]["score"]
    # smoothing formula: n=4, avg 5, compound 0 -> raw = 0.7 + 0.15 = 0.85
    assert by[("printer", "try_it")]["score"] == round((3 + 4 * 0.85) / 9, 4)
    assert s["format_rank"]["printer"] == ["try_it", "see_it", "hear_it", "read_it"]
    assert s["format_rank"]["email"] == FORMATS
    assert s["flagged"] == [{"category": "printer", "format": "read_it",
                             "reason": "avg_stars < 2.5 over 3+ ratings"}]
    assert s["by_format"]["try_it"]["count"] == 4 and s["by_category"]["wifi"]["avg_stars"] == 3.0
    assert s["by_week"] == [{"week": "2026-W47", "count": 8, "avg_stars": pytest.approx(3.25, abs=0.01)}]
    assert fb.format_rank(s) == s["format_rank"]


def test_sentiment_callable_and_no_text_leak():
    def fake(text):
        return {"compound": -0.8, "label": "negative"} if "bad" in text else {"compound": 0.8, "label": "positive"}
    rows = [row(5, comment="great"), row(2, comment="bad bad"), row(4)]
    s = fb.summarize(rows, sentiment=fake)
    assert s["sentiment"] == {"positive": 1, "neutral": 0, "negative": 1}
    assert s["items"][0]["avg_compound"] == 0.0  # (0.8 - 0.8) / 2
    assert "great" not in json.dumps(s) and "printer print" not in json.dumps(s)


def test_training_rows():
    rows = [row(5), row(5), row(3, question="my laptop is slow today"), row(4, question="short"),
            row(4, cat="wifi", question="wifi drops every hour")]
    assert fb.training_rows(rows) == [("why wont my printer print", "printer"), ("wifi drops every hour", "wifi")]


def test_http_error_returns_empty_and_token_never_printed(monkeypatch, capsys):
    secret = "SECRET-TOKEN-123"
    def boom(*a, **k):
        raise fb.urllib.error.URLError("down")
    monkeypatch.setattr(fb.urllib.request, "urlopen", boom)
    monkeypatch.delenv("HELPMATE_FEEDBACK_FILE", raising=False)
    assert fb.load_feedback(token=secret, site_id="site1") == []
    out = capsys.readouterr()
    assert secret not in out.out + out.err


def test_api_pagination_verified_only(monkeypatch, capsys):
    secret = "SECRET-TOKEN-456"
    urls, headers = [], []
    pages = {1: [{"id": "a", "created_at": "2026-11-01T00:00:00Z", "data": row(5)}] * 100,
             2: [{"id": "b", "created_at": "2026-11-02T00:00:00Z", "data": row(4)}], 3: []}

    class Resp:
        def __init__(self, payload): self.p = payload
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self, *a): return json.dumps(self.p).encode()

    def fake(req, timeout=0):
        urls.append(req.full_url); headers.append(req.get_header("Authorization"))
        if req.full_url.endswith("/forms"):
            return Resp([{"id": "f1", "name": "other"}, {"id": "f2", "name": "rating"}])
        return Resp(pages[int(req.full_url.rsplit("page=", 1)[1])])

    monkeypatch.setattr(fb.urllib.request, "urlopen", fake)
    monkeypatch.delenv("HELPMATE_FEEDBACK_FILE", raising=False)
    rows = fb.load_feedback(token=secret, site_id="site1")
    assert len(rows) == 101
    assert all("state=verified" in u and "/forms/f2/" in u for u in urls[1:])
    assert set(headers) == {f"Bearer {secret}"}
    assert secret not in "".join(urls)
    out = capsys.readouterr()
    assert secret not in out.out + out.err


def test_get_sentiment_never_raises():
    assert fb.get_sentiment() is None or callable(fb.get_sentiment())


def test_source_has_no_token_logging():
    src = (ROOT / "pipeline" / "feedback.py").read_text()
    assert "print(" not in src.replace("print(f\"[feedback] {msg}\"", "")
