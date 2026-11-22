"""Shared constants and the JSON writer for HelpMate (stdlib only, plan section 2)."""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

CATEGORIES: list[tuple[str, str]] = [
    ("printer", "Printer"),
    ("email", "Email"),
    ("wifi", "Wi-Fi & Internet"),
    ("passwords", "Passwords & Login"),
    ("slow", "Slow computer"),
    ("phone_apps", "Phone & Apps"),
    ("files", "Files & Storage"),
    ("video_calls", "Video calls"),
]
CATEGORY_IDS: list[str] = [c for c, _ in CATEGORIES]
DISPLAY_NAMES: dict[str, str] = dict(CATEGORIES)

FORMATS = ["see_it", "hear_it", "try_it", "read_it"]
LIBRARIES = ("NLTK", "spaCy", "Neural network", "NLTK + spaCy")
SCHEMA_VERSION = 1


def utc_now() -> str:
    """Current UTC time like 2026-11-22T10:00:00Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path, payload: dict, library: str, compact: bool = False) -> pathlib.Path:
    """Write payload with generated_at, library and schema_version added."""
    if library not in LIBRARIES:
        raise ValueError(f"library must be one of {LIBRARIES}, got {library!r}")
    data = dict(payload)
    data["generated_at"] = utc_now()
    data["library"] = library
    data["schema_version"] = SCHEMA_VERSION
    data.setdefault("items", [])
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        if compact:
            json.dump(data, f, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        else:
            json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=1)
    return p
