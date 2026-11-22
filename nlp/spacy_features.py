"""spaCy features for HelpMate. BUILD TIME ONLY: spaCy never runs in the browser.

Everything here is written for spaCy v3 (en_core_web_sm). spaCy itself is imported
inside build_nlp(), so this module can be imported (and export_patterns used) without spaCy.
Results are labelled "spaCy" when written to site/data/.
"""
from __future__ import annotations

import itertools
import json
import re
from pathlib import Path

ENTITY_LABELS = ("DEVICE", "APP", "OS", "ERROR_CODE")
EXTRA_LABELS = ("ORG", "PRODUCT")  # kept from the statistical NER

_REPO = Path(__file__).resolve().parent.parent
PATTERNS_PATH = str(_REPO / "nlp" / "patterns" / "it_entities.jsonl")
HINTS_PATH = str(_REPO / "nlp" / "patterns" / "category_hints.json")

# Hand-written JavaScript regexes (the ruler's REGEX token patterns cannot be exported).
JS_REGEX: list[dict] = [
    {"label": "ERROR_CODE", "pattern": r"\b0x[0-9a-f]{4,8}\b", "flags": "i"},
    {"label": "ERROR_CODE", "pattern": r"\b(?:http\s+)?error\s*(?:code\s*)?[45][0-9]{2}\b", "flags": "i"},
    {"label": "ERROR_CODE", "pattern": r"\b[45][0-9]{2}\s+error\b", "flags": "i"},
    {"label": "ERROR_CODE", "pattern": r"\b[a-z]+(?:_[a-z0-9]+){2,}\b", "flags": "i"},
]

NEGATION_WORDS = frozenset({"not", "n't", "never", "no", "cannot", "nor"})
# Adjectives that are not problems unless negated ("the wifi is fine on my phone").
GOOD_WORDS = frozenset({"fine", "good", "great", "ok", "okay", "fast", "new", "ready", "happy", "easy",
                        "better", "best", "nice", "sure", "available", "free", "possible", "able"})
# Verbs that describe a problem even without "not" ("my wifi keeps dropping", "screen froze").
PROBLEM_VERBS = frozenset({
    "fail", "crash", "freeze", "hang", "stop", "drop", "disconnect", "lose", "lag", "jam", "break", "die",
    "disappear", "vanish", "restart", "reboot", "flicker", "glitch", "stall", "overheat", "forget", "lock",
    "block", "miss", "stutter", "buffer", "timeout", "error",
})
# Verbs that take another verb and describe a repeating problem: "keeps dropping" -> "keep drop".
ASPECT_VERBS = frozenset({"keep", "start", "stop", "continue", "fail", "refuse", "seem", "begin"})
# Nouns that name a problem: "printer error", "wifi problem", "screen freeze".
PROBLEM_NOUNS = frozenset({"error", "problem", "issue", "glitch", "crash", "freeze", "failure", "bug", "lag",
                           "outage", "delay"})
# Words used by the verb-less fallback ("printer broken", "wifi down").
PROBLEM_WORDS = frozenset({
    "broken", "slow", "frozen", "offline", "down", "dead", "stuck", "jammed", "crashed", "blank", "missing",
    "locked", "failing", "failed", "faulty", "useless", "unavailable", "disconnected", "dropping", "freezing",
    "laggy", "glitchy", "error", "wrong", "full", "empty", "loud", "hot", "black", "gone", "unresponsive",
})
BE_LIKE = frozenset({"be", "seem", "look", "become", "get", "go", "stay", "say", "show", "display", "read",
                     "turn", "remain", "appear", "feel", "sound", "keep"})


# --------------------------------------------------------------------------- pipeline
def load_patterns(patterns_path: str = PATTERNS_PATH) -> list[dict]:
    """Read the JSONL pattern file (one JSON object per line; blank lines ignored)."""
    out = []
    with open(patterns_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def build_nlp(model: str = "en_core_web_sm", patterns_path: str = PATTERNS_PATH):
    """en_core_web_sm plus an EntityRuler placed before "ner" (so the model respects its spans)."""
    import spacy  # imported here so the rest of the module works without spaCy

    nlp = spacy.load(model)
    ruler = nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": "LOWER"})
    ruler.add_patterns(load_patterns(patterns_path))
    return nlp


# --------------------------------------------------------------------------- entities
def entities(doc) -> list[dict]:
    """IT entities (DEVICE, APP, OS, ERROR_CODE) plus ORG and PRODUCT from the model."""
    keep = set(ENTITY_LABELS) | set(EXTRA_LABELS)
    out = []
    for ent in doc.ents:
        if ent.label_ not in keep:
            continue
        out.append({
            "text": ent.text,
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char,
            "id": ent.ent_id_ or ent.text.lower(),
        })
    return out


# --------------------------------------------------------------------------- problems
def _entity_map(doc) -> dict:
    """token index -> entity span, for the IT labels only."""
    m = {}
    for ent in doc.ents:
        if ent.label_ in ENTITY_LABELS:
            for tok in ent:
                m[tok.i] = ent
    return m


def _is_negated(tok) -> bool:
    return any(c.dep_ == "neg" or c.lower_ in NEGATION_WORDS for c in tok.children)


def _thing_name(tok, ents) -> str | None:
    """Name of a thing, or None when the token is not a usable thing (pronoun, stop word, number)."""
    if tok is None:
        return None
    if tok.i in ents:
        ent = ents[tok.i]
        if ent.label_ in ("ERROR_CODE",):
            return None
        return ent.root.lemma_.lower()
    if tok.pos_ not in ("NOUN", "PROPN") or tok.is_stop:
        return None
    parts = [c.lemma_.lower() for c in tok.lefts if c.dep_ == "compound" and c.pos_ in ("NOUN", "PROPN")]
    return " ".join(parts + [tok.lemma_.lower()])


def _first_thing(candidates, ents):
    for c in candidates:
        name = _thing_name(c, ents)
        if name:
            return name
    return None


def _thing_for(tok, ents, allow_loose: bool):
    """Subject first; with allow_loose also the object or the noun after a preposition."""
    subj = [c for c in tok.children if c.dep_ in ("nsubj", "nsubjpass")]
    name = _first_thing(subj, ents)
    if name or not allow_loose:
        return name
    objs = [c for c in tok.children if c.dep_ in ("dobj", "obj", "attr")]
    name = _first_thing(objs, ents)
    if name:
        return name
    pobjs = [g for c in tok.children if c.dep_ == "prep" for g in c.children if g.dep_ == "pobj"]
    return _first_thing(pobjs, ents)


def _add(out: list, seen: set, thing: str | None, problem: str, negated: bool) -> None:
    if not thing:
        return
    text = ("not " if negated else "") + problem
    key = (thing, text)
    if key in seen:
        return
    seen.add(key)
    out.append({"thing": thing, "problem": text, "negated": negated})


def problems(doc) -> list[dict]:
    """(thing, problem) pairs from the dependency parse, keeping negation.

    "My printer won't print"        -> thing printer, problem "not print", negated True
    "The wifi keeps dropping"       -> thing wifi, problem "keep drop"
    "The printer is broken"         -> thing printer, problem "broken"
    "Printer error 0x000003eb"      -> thing printer, problem "error"
    "printer broken" (no verb)      -> thing printer, problem "broken" (lexicon fallback)
    """
    ents = _entity_map(doc)
    out: list[dict] = []
    seen: set = set()
    if not doc.has_annotation("DEP"):
        return out

    for tok in doc:
        # 1. adjective with its own subject: "printer broken"
        if tok.pos_ == "ADJ" and any(c.dep_ in ("nsubj", "nsubjpass") for c in tok.children):
            neg = _is_negated(tok)
            if neg or tok.lower_ not in GOOD_WORDS:
                _add(out, seen, _thing_for(tok, ents, False), tok.lower_, neg)
            continue

        if tok.pos_ not in ("VERB", "AUX"):
            continue
        neg = _is_negated(tok)

        # 2. copula-like head with an adjective: "is broken", "says offline", "went blank"
        adjs = [c for c in tok.children if c.dep_ in ("acomp", "oprd") and c.pos_ == "ADJ"]
        if adjs and tok.lemma_ in BE_LIKE:
            adj = adjs[0]
            neg = neg or _is_negated(adj)
            if neg or adj.lower_ not in GOOD_WORDS:
                _add(out, seen, _thing_for(tok, ents, False), adj.lower_, neg)
            continue

        # 3. noun naming a problem: "printer shows error", "has a problem"
        pn = [c for c in tok.children if c.dep_ in ("dobj", "obj", "attr") and c.lemma_.lower() in PROBLEM_NOUNS]
        if pn:
            _add(out, seen, _thing_for(tok, ents, False), pn[0].lemma_.lower(), neg)
            continue

        if tok.pos_ != "VERB" or tok.lemma_ in ("be", "do", "have"):
            continue

        # 4. aspect verb + verb: "keeps dropping" -> "keep drop"
        xcomps = [c for c in tok.children if c.dep_ == "xcomp" and c.pos_ == "VERB"]
        if tok.lemma_ in ASPECT_VERBS and xcomps:
            x = xcomps[0]
            neg = neg or _is_negated(x)
            thing = _thing_for(tok, ents, True) or _thing_for(x, ents, True)
            _add(out, seen, thing, f"{tok.lemma_.lower()} {x.lemma_.lower()}", neg)
            continue

        # 5. plain verb: only when negated or it names a problem ("won't print", "crashed")
        if neg or tok.lemma_.lower() in PROBLEM_VERBS:
            _add(out, seen, _thing_for(tok, ents, True), tok.lemma_.lower(), neg)

    # 6. compound problem nouns: "printer error", "wifi problem"
    for tok in doc:
        if tok.lemma_.lower() in PROBLEM_NOUNS and tok.pos_ == "NOUN":
            comps = [c for c in tok.lefts if c.dep_ == "compound"]
            if comps:
                name = _thing_name(comps[-1], ents) or (comps[-1].lemma_.lower() if comps[-1].pos_ in ("NOUN", "PROPN") else None)
                _add(out, seen, name, tok.lemma_.lower(), False)

    # 7. verb-less fallback: an IT entity next to a problem word ("printer broken", "wifi down")
    if not out:
        ent_list = [e for e in doc.ents if e.label_ in ("DEVICE", "APP", "OS")]
        neg_doc = any(t.lower_ in NEGATION_WORDS for t in doc)
        for ent in ent_list:
            for tok in doc:
                if tok.lower_ in PROBLEM_WORDS and tok.i not in range(ent.start, ent.end) and abs(tok.i - ent.end) <= 3:
                    _add(out, seen, ent.root.lemma_.lower(), tok.lower_, neg_doc)
                    break
    return out


# --------------------------------------------------------------------------- tags
def tags(doc) -> list[str]:
    """Sorted unique lower-case lemmas of noun-chunk roots and DEVICE/APP/OS entities.

    No stop words or pronouns, and at least 3 characters. Entities use their pattern id
    ("google drive" variants share one tag), so "printers" and "HP printer" both give "printer".
    """
    found: set[str] = set()
    for chunk in doc.noun_chunks:
        root = chunk.root
        if root.pos_ not in ("NOUN", "PROPN") or root.is_stop:
            continue
        found.add(root.lemma_.lower())
    for ent in doc.ents:
        if ent.label_ in ("DEVICE", "APP", "OS"):
            found.add((ent.ent_id_ or ent.root.lemma_).lower().replace("_", " "))
    return sorted(t for t in found if len(t) >= 3 and re.search(r"[a-z]", t))


def analyze(texts: list[str], nlp, batch_size: int = 64) -> list[dict]:
    """Run nlp.pipe once and return [{"entities", "problems", "tags"}] in input order."""
    out = []
    for doc in nlp.pipe(texts, batch_size=batch_size):
        out.append({"entities": entities(doc), "problems": problems(doc), "tags": tags(doc)})
    return out


# --------------------------------------------------------------------------- export for the browser
_PLURAL_ES = ("s", "x", "ch", "sh")
_MAX_PHRASES = 50


def _variants(token: dict):
    """Lower-case strings one pattern token can produce, or None if it cannot be exported.

    Returns "REGEX" for regex tokens (covered by JS_REGEX, not counted as skipped).
    """
    op = token.get("OP")
    if op not in (None, "?"):
        return None
    attrs = [k for k in token if k != "OP"]
    if len(attrs) != 1 or attrs[0] not in ("LOWER", "TEXT", "LEMMA"):
        return None
    attr = attrs[0]
    value = token[attr]
    if isinstance(value, dict):
        if set(value) == {"REGEX"}:
            return "REGEX"
        if set(value) != {"IN"}:
            return None
        values = list(value["IN"])
    elif isinstance(value, str):
        values = [value]
    else:
        return None
    out: list[str] = []
    for v in values:
        v = v.lower()
        out.append(v)
        if attr == "LEMMA":
            out.append(v + ("es" if v.endswith(_PLURAL_ES) else "s"))
    if op == "?":
        out.append("")
    return out


def _pattern_phrases(pattern):
    """(phrases, status): status is "ok", "regex" or "skipped"."""
    if isinstance(pattern, str):
        return [pattern.lower()], "ok"
    if not isinstance(pattern, list):
        return [], "skipped"
    choices = []
    for tok in pattern:
        if not isinstance(tok, dict):
            return [], "skipped"
        v = _variants(tok)
        if v == "REGEX":
            return [], "regex"
        if v is None:
            return [], "skipped"
        choices.append(v)
    size = 1
    for c in choices:
        size *= len(c)
    if size > _MAX_PHRASES:
        return [], "skipped"
    phrases = {" ".join(p for p in combo if p).strip() for combo in itertools.product(*choices)}
    phrases.discard("")
    return sorted(phrases), "ok"


def export_patterns(path: str, patterns_path: str = PATTERNS_PATH, hints_path: str = HINTS_PATH) -> dict:
    """Write site/data/entity_patterns.json (library "spaCy") and return the payload."""
    from nlp.common import write_json

    hints: dict = {}
    if hints_path and Path(hints_path).exists():
        with open(hints_path, encoding="utf-8") as fh:
            hints = json.load(fh)

    grouped: dict[str, dict] = {}
    skipped = 0
    for pat in load_patterns(patterns_path):
        phrases, status = _pattern_phrases(pat.get("pattern"))
        if status == "regex":
            continue
        if status == "skipped" or not phrases:
            skipped += 1
            continue
        item_id = pat.get("id") or phrases[0]
        item = grouped.setdefault(item_id, {"id": item_id, "label": pat["label"], "phrases": set()})
        item["phrases"].update(phrases)

    items = []
    for item_id in sorted(grouped):
        item = grouped[item_id]
        items.append({
            "id": item_id,
            "label": item["label"],
            "phrases": sorted(item["phrases"]),
            "category_hint": hints.get(item_id),
        })
    payload = {
        "labels": list(ENTITY_LABELS),
        "items": items,
        "regex": JS_REGEX,
        "skipped_patterns": skipped,
    }
    write_json(path, payload, "spaCy")
    return payload
