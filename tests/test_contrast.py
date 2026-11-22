"""WCAG 2.2 contrast check for site/css/design-tokens.css (owner: Iris).

Reads the hex values of the CSS custom properties and asserts every text pair is
>= 4.5:1 and every graphic pair is >= 3:1. Stdlib only.
"""
import pathlib
import re

import pytest

TOKENS = pathlib.Path(__file__).resolve().parents[1] / "site" / "css" / "design-tokens.css"


def _vars() -> dict:
    css = TOKENS.read_text(encoding="utf-8")
    out = {}
    for name, value in re.findall(r"--([a-z0-9-]+):\s*([^;]+);", css):
        out[name] = value.strip()
    return out


def _resolve(vs: dict, name: str, depth: int = 0) -> str:
    v = vs[name]
    m = re.fullmatch(r"var\(--([a-z0-9-]+)\)", v.split("/*")[0].strip())
    if m and depth < 5:
        return _resolve(vs, m.group(1), depth + 1)
    m = re.match(r"(#[0-9A-Fa-f]{6})", v)
    assert m, f"--{name} is not a hex color: {v}"
    return m.group(1)


def _lum(h: str) -> float:
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# (foreground token, background token, minimum ratio)
PAIRS = [
    ("navy", "bg", 4.5), ("navy", "white", 4.5),
    ("text-muted", "bg", 4.5), ("text-muted", "white", 4.5),
    ("link", "bg", 4.5), ("link", "white", 4.5), ("link-hover", "bg", 4.5),
    ("text-on-dark", "navy", 4.5),
    ("white", "blue-ink", 4.5), ("white", "coral-ink", 4.5),
    ("white", "teal-ink", 4.5), ("white", "purple-ink", 4.5),
    ("blue-ink", "bg", 4.5), ("coral-ink", "bg", 4.5),
    ("teal-ink", "bg", 4.5), ("purple-ink", "bg", 4.5), ("amber-ink", "bg", 4.5),
    ("navy", "blue-tint", 4.5), ("navy", "coral-tint", 4.5), ("navy", "teal-tint", 4.5),
    ("navy", "purple-tint", 4.5), ("navy", "amber-tint", 4.5),
    ("text-muted", "blue-tint", 4.5), ("text-muted", "coral-tint", 4.5),
    ("text-muted", "teal-tint", 4.5), ("text-muted", "purple-tint", 4.5),
    # coral-ink on coral-tint is only about 4.4:1, so CSS never uses it; use navy there.
    ("blue-ink", "blue-tint", 4.5),
    ("teal-ink", "teal-tint", 4.5), ("purple-ink", "purple-tint", 4.5),
    ("warn-ink", "warn-tint", 4.5), ("error-ink", "error-tint", 4.5),
    ("ok-ink", "ok-tint", 4.5),
    ("badge-nltk-text", "badge-nltk-bg", 4.5), ("badge-spacy-text", "badge-spacy-bg", 4.5),
    ("badge-nn-text", "badge-nn-bg", 4.5), ("badge-both-text", "badge-both-bg", 4.5),
    ("btn-primary-text", "btn-primary-bg", 4.5), ("btn-primary-text", "btn-primary-bg-hover", 4.5),
    ("navy", "coral", 4.5), ("navy", "teal", 4.5),            # navy text on bright fills
    # graphics and borders, 3:1
    ("line-strong", "bg", 3.0), ("line-strong", "white", 3.0),
    ("amber-ink", "white", 3.0), ("focus-color", "bg", 3.0), ("focus-color-on-dark", "navy", 3.0),
    ("chart-1", "white", 3.0), ("chart-2", "white", 3.0), ("chart-3", "white", 3.0),
    ("chart-4", "white", 3.0), ("chart-5", "white", 3.0),
    ("blue", "bg", 3.0),                                       # large text / icon only
]


@pytest.mark.parametrize("fg,bg,minimum", PAIRS)
def test_pair(fg, bg, minimum):
    vs = _vars()
    r = ratio(_resolve(vs, fg), _resolve(vs, bg))
    assert r >= minimum, f"{fg} on {bg} is {r:.2f}:1, needs {minimum}:1"
