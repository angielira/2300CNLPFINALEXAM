"""Ratings loop (plan section 4.4): read Netlify Forms ratings, score them, rank formats.

Standard library only. nltk is optional and imported lazily (see get_sentiment).
The API token is sent only in a request header and is never printed or logged.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable

try:  # works as `pipeline.feedback` and when run with the repo root on sys.path
    from nlp.common import CATEGORY_IDS, FORMATS
except ImportError:  # pragma: no cover
    CATEGORY_IDS = ["printer", "email", "wifi", "passwords", "slow", "phone_apps", "files", "video_calls"]
    FORMATS = ["see_it", "hear_it", "try_it", "read_it"]

API = "https://api.netlify.com/api/v1"
SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "feedback_sample.json"
PRIOR = 0.6          # smoothing target
PRIOR_WEIGHT = 5     # worth of 5 imaginary ratings
FLAG_MAX_STARS = 2.5
FLAG_MIN_COUNT = 3
MIN_QUESTION_LEN = 8

_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"(?<![\w])\+?\d[\d\s().\-]{7,}\d(?![\w])")


def _warn(msg: str) -> None:
    print(f"[feedback] {msg}", file=sys.stderr)


def mask_pii(text) -> str:
    """Replace email addresses and phone-like numbers with placeholders."""
    if not isinstance(text, str):
        return ""
    text = _EMAIL.sub("[email removed]", text)
    return _PHONE.sub("[phone removed]", text)


def _normalize(row: dict) -> dict | None:
    """Turn a raw row (flat, or Netlify style with a 'data' dict) into the plan shape, or None."""
    data = row.get("data") if isinstance(row.get("data"), dict) else row
    try:
        stars = int(str(data.get("stars", "")).strip())
    except (TypeError, ValueError):
        return None
    if not 1 <= stars <= 5:
        return None
    category = str(data.get("category", "")).strip()
    fmt = str(data.get("format", "")).strip()
    if category not in CATEGORY_IDS or fmt not in FORMATS:
        return None
    out = {
        "id": str(row.get("id", "")),
        "created_at": str(row.get("created_at", "")),
        "stars": stars,
        "comment": mask_pii(data.get("comment", "")).strip()[:500],
        "question": mask_pii(data.get("question", "")).strip()[:300],
        "category": category,
        "format": fmt,
    }
    if row.get("sample"):
        out["sample"] = True
    return out


def _get_json(url: str, token: str):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _fetch_netlify(token: str, site_id: str, form_name: str) -> list[dict]:
    forms = _get_json(f"{API}/sites/{site_id}/forms", token)
    form_id = next((f.get("id") for f in forms if f.get("name") == form_name), None)
    if not form_id:
        _warn(f"No form named {form_name!r} yet. Using no ratings.")
        return []
    rows: list[dict] = []
    page = 1
    while page <= 200:  # hard stop: 20,000 submissions
        batch = _get_json(f"{API}/forms/{form_id}/submissions?state=verified&per_page=100&page={page}", token)
        if not batch:
            break
        rows.extend(batch)
        page += 1
    return rows


def _read_file(path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return raw.get("items", []) if isinstance(raw, dict) else raw


def load_feedback(token: str | None = None, site_id: str | None = None, path: str | None = None,
                  form_name: str = "rating", sample_fallback: bool = True) -> list[dict]:
    """Return normalized, PII-masked ratings.

    Order: file (path or HELPMATE_FEEDBACK_FILE) -> Netlify API (token + site id) ->
    data/feedback_sample.json when there is no token (sample_fallback=True; rows are marked sample)
    -> []. HTTP problems give a warning and [].
    """
    path = path or os.environ.get("HELPMATE_FEEDBACK_FILE")
    token = token or os.environ.get("NETLIFY_API_TOKEN")
    site_id = site_id or os.environ.get("SITE_ID")
    try:
        if path:
            raw = _read_file(path)
        elif token and site_id:
            raw = _fetch_netlify(token, site_id, form_name)
        elif token:
            _warn("NETLIFY_API_TOKEN is set but SITE_ID is not. Using no ratings.")
            return []
        elif sample_fallback and SAMPLE_PATH.exists():
            _warn("No NETLIFY_API_TOKEN: using data/feedback_sample.json (fake sample ratings).")
            raw = _read_file(SAMPLE_PATH)
        else:
            return []
    except urllib.error.HTTPError as e:
        _warn(f"Netlify answered HTTP {e.code}. Using no ratings.")
        return []
    except (urllib.error.URLError, OSError, ValueError, TimeoutError) as e:
        _warn(f"Could not load ratings ({type(e).__name__}). Using no ratings.")
        return []
    rows = [_normalize(r) for r in raw if isinstance(r, dict)]
    return [r for r in rows if r]


def get_sentiment() -> Callable[[str], dict] | None:
    """nltk_features.satisfaction if nltk and VADER data work here, else None."""
    try:
        from nlp import nltk_features
        nltk_features.satisfaction("ok")  # triggers the lazy data load
        return nltk_features.satisfaction
    except Exception as e:  # ImportError, LookupError (data), anything odd
        _warn(f"Comment sentiment skipped ({type(e).__name__}).")
        return None


def _score(avg_stars: float, avg_compound: float, n: int) -> float:
    raw = 0.7 * (avg_stars - 1) / 4 + 0.3 * (avg_compound + 1) / 2
    return round((PRIOR_WEIGHT * PRIOR + n * raw) / (PRIOR_WEIGHT + n), 4)


def _week(created_at: str) -> str | None:
    try:
        d = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def summarize(feedback: list[dict], sentiment: Callable[[str], dict] | None = None) -> dict:
    """ratings_summary payload (no generated_at). Aggregates only: no comment or question text."""
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    weeks: dict[str, list[int]] = defaultdict(list)
    counts = {"positive": 0, "neutral": 0, "negative": 0}
    compounds: dict[int, float] = {}
    for i, r in enumerate(feedback):
        groups[(r["category"], r["format"])].append(r)
        wk = _week(r.get("created_at", ""))
        if wk:
            weeks[wk].append(r["stars"])
        if sentiment and r.get("comment"):
            try:
                s = sentiment(r["comment"])
                compounds[i] = float(s["compound"])
                counts[s["label"]] += 1
            except Exception:
                pass
    index = {id(r): i for i, r in enumerate(feedback)}

    def stats(rows: list[dict]) -> tuple[float, float]:
        stars = sum(r["stars"] for r in rows) / len(rows)
        comps = [compounds[index[id(r)]] for r in rows if index[id(r)] in compounds]
        return stars, (sum(comps) / len(comps) if comps else 0.0)

    items, flagged, scores = [], [], {}
    for cat in CATEGORY_IDS:
        for fmt in FORMATS:
            rows = groups.get((cat, fmt))
            if not rows:
                continue
            stars, comp = stats(rows)
            score = _score(stars, comp, len(rows))
            scores[(cat, fmt)] = score
            items.append({"category": cat, "format": fmt, "count": len(rows), "avg_stars": round(stars, 2),
                          "avg_compound": round(comp, 3), "score": score})
            if len(rows) >= FLAG_MIN_COUNT and stars < FLAG_MAX_STARS:
                flagged.append({"category": cat, "format": fmt,
                                "reason": f"avg_stars < {FLAG_MAX_STARS} over {FLAG_MIN_COUNT}+ ratings"})

    def rollup(key: str, order: list[str]) -> dict:
        out = {}
        for k in order:
            rows = [r for r in feedback if r[key] == k]
            if rows:
                stars, comp = stats(rows)
                out[k] = {"count": len(rows), "avg_stars": round(stars, 2), "avg_compound": round(comp, 3)}
        return out

    rank = {cat: sorted(FORMATS, key=lambda f: (-scores.get((cat, f), PRIOR), FORMATS.index(f)))
            for cat in CATEGORY_IDS}
    return {
        "total": len(feedback),
        "items": items,
        "by_category": rollup("category", CATEGORY_IDS),
        "by_format": rollup("format", FORMATS),
        "by_week": [{"week": w, "count": len(s), "avg_stars": round(sum(s) / len(s), 2)}
                    for w, s in sorted(weeks.items())],
        "format_rank": rank,
        "flagged": flagged,
        "sentiment": dict(counts) if sentiment else {"positive": None, "neutral": None, "negative": None},
    }


def format_rank(summary: dict) -> dict[str, list[str]]:
    """Per-category format order for answers.json (defaults to FORMATS order)."""
    stored = summary.get("format_rank") or {}
    return {cat: list(stored.get(cat) or FORMATS) for cat in CATEGORY_IDS}


def training_rows(feedback: list[dict], include_sample: bool = False) -> list[tuple[str, str]]:
    """(question, category) for well-rated real questions. Fake sample rows are skipped by default."""
    seen, out = set(), []
    for r in feedback:
        q = r.get("question", "").strip()
        if (r["stars"] >= 4 and r["category"] in CATEGORY_IDS and len(q) >= MIN_QUESTION_LEN
                and (include_sample or not r.get("sample")) and q.lower() not in seen):
            seen.add(q.lower())
            out.append((q, r["category"]))
    return out
