"""HelpMate build: runs NLTK, spaCy and training, and writes every static file (plan section 4.5).

Usage (repo root):  python pipeline/build.py [--out site] [--allow-missing]
Same command locally and on Netlify. --allow-missing is for local tests only.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlp.common import CATEGORY_IDS, FORMATS, write_json  # noqa: E402

NLTK_DIR = ROOT / ".cache" / "nltk_data"
NLTK_PACKAGES = ["stopwords", "vader_lexicon", "wordnet", "omw-1.4"]
PY_FILES = ["nlp/__init__.py", "nlp/nltk_features.py", "nlp/classifier.py"]
NLTK_VERSION_PIN = "3.9.4"


class BuildError(Exception):
    pass


def say(msg: str) -> None:
    print(f"[build] {msg}", flush=True)


# ---------- step 1: content ----------
def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BuildError(f"cannot read {path}: {e}")


def validate_content(answers: dict, lessons: dict) -> None:
    a_items, l_items = answers.get("items", []), lessons.get("items", [])
    if [a.get("category") for a in a_items] != CATEGORY_IDS:
        raise BuildError("answers.json: need exactly one item per category, in CATEGORIES order")
    if [l.get("category") for l in l_items] != CATEGORY_IDS:
        raise BuildError("lessons.json: need exactly one item per category, in CATEGORIES order")
    for a in a_items:
        c = a["category"]
        for f in FORMATS:
            if f not in a:
                raise BuildError(f"answers.json[{c}]: missing format {f}")
        lens = {len(a["see_it"]["steps"]), len(a["try_it"]["steps"]),
                len(a["hear_it"]["script"]), len(a["read_it"]["checklist"])}
        if len(lens) != 1 or not 4 <= lens.pop() <= 8:
            raise BuildError(f"answers.json[{c}]: formats need the same step count (4-8)")
        for s in a["see_it"]["steps"]:
            if s.get("image") and not s.get("alt"):
                raise BuildError(f"answers.json[{c}]: image without alt text")
    for l in l_items:
        c = l["category"]
        steps = l.get("steps", [])
        if [s.get("n") for s in steps] != list(range(1, 11)):
            raise BuildError(f"lessons.json[{c}]: need exactly 10 steps numbered 1-10")
        for s in steps:
            ch = s.get("choices", [])
            if len(ch) != 3 or not isinstance(s.get("answer"), int) or not 0 <= s["answer"] < 3:
                raise BuildError(f"lessons.json[{c}] step {s.get('n')}: need 3 choices and answer 0-2")


# ---------- data ----------
def read_seed() -> list[dict]:
    p = ROOT / "data" / "seed_questions.csv"
    if not p.exists():
        raise BuildError(f"missing {p}")
    with open(p, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    bad = [r for r in rows if r["category"] not in CATEGORY_IDS]
    if bad:
        raise BuildError(f"seed_questions.csv has unknown categories, e.g. {bad[0]['category']!r}")
    return rows


def read_tickets() -> list[tuple[str, str]]:
    p = ROOT / "data" / "tickets_sample.csv"
    if not p.exists():
        say("data/tickets_sample.csv not found: training on seed questions only")
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return [(r["text"], r["category"]) for r in csv.DictReader(f)
                if r.get("category") in CATEGORY_IDS and r.get("text")]


def read_gold() -> list[dict] | None:
    p = ROOT / "data" / "spacy_gold.jsonl"
    if not p.exists():
        return None
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---------- step 2: NLTK ----------
def setup_nltk(out: Path, allow_missing: bool) -> bool:
    """Download NLTK data, copy the browser files. Returns True when NLTK is ready."""
    try:
        import nltk
    except ImportError:
        if allow_missing:
            say("SKIPPED: nltk is not installed (--allow-missing)")
            return False
        raise BuildError("nltk is not installed. Run: pip install -r requirements.txt")
    if nltk.__version__ != NLTK_VERSION_PIN:
        say(f"WARNING: nltk {nltk.__version__} differs from the browser's {NLTK_VERSION_PIN}; "
            "tokens may differ")
    NLTK_DIR.mkdir(parents=True, exist_ok=True)
    try:
        for pkg in NLTK_PACKAGES:
            if not nltk.download(pkg, download_dir=str(NLTK_DIR), quiet=True):
                raise BuildError(f"nltk.download('{pkg}') failed. Check the network.")
    except BuildError:
        if allow_missing:
            say("SKIPPED: NLTK data could not be downloaded (--allow-missing)")
            return False
        raise
    from nlp import nltk_features
    nltk_features.use_data_dir(str(NLTK_DIR))
    return True


def _extract(zip_path: Path, member: str, dest: Path) -> None:
    with zipfile.ZipFile(zip_path) as z:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(z.read(member))


def copy_browser_nltk(out: Path) -> list[str]:
    """Copy only stopwords and the VADER lexicon to <out>/nltk_data. Returns manifest items."""
    dest_root = out / "nltk_data"
    if dest_root.exists():
        shutil.rmtree(dest_root)
    items = []
    sw = ("corpora/stopwords/english", NLTK_DIR / "corpora/stopwords/english",
          NLTK_DIR / "corpora/stopwords.zip", "stopwords/english")
    vd = ("sentiment/vader_lexicon/vader_lexicon.txt",
          NLTK_DIR / "sentiment/vader_lexicon/vader_lexicon.txt",
          NLTK_DIR / "sentiment/vader_lexicon.zip", "vader_lexicon/vader_lexicon.txt")
    for rel, plain, zp, member in (sw, vd):
        dest = dest_root / rel
        if plain.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(plain, dest)
        elif zp.exists():
            _extract(zp, member, dest)
        else:
            raise BuildError(f"NLTK file not found for the browser: {rel}")
        items.append(rel)
    return items


# ---------- spaCy ----------
def setup_spacy(allow_missing: bool):
    try:
        from nlp import spacy_features
        nlp = spacy_features.build_nlp("en_core_web_sm", str(ROOT / "nlp/patterns/it_entities.jsonl"))
        return spacy_features, nlp
    except (ImportError, OSError) as e:
        if allow_missing:
            say(f"SKIPPED: spaCy is not available ({type(e).__name__}) (--allow-missing)")
            return None, None
        raise BuildError(f"spaCy or en_core_web_sm is missing ({e}). Run: pip install -r "
                         "requirements.txt && python -m spacy download en_core_web_sm")


# ---------- feedback ----------
def get_feedback(nltk_ok: bool, allow_missing: bool):
    sentiment = None
    if nltk_ok:
        from nlp import nltk_features
        sentiment = nltk_features.satisfaction
    try:
        from pipeline import feedback as fb
    except ImportError as e:
        if not allow_missing:
            raise BuildError(f"pipeline/feedback.py is missing: {e}")
        say("SKIPPED: pipeline/feedback.py not found; using empty feedback")
        return _empty_summary(), []
    rows: list[dict] = []
    token_set = bool(os.environ.get("NETLIFY_API_TOKEN"))
    sample = ROOT / "data" / "feedback_sample.json"
    if token_set:
        rows = fb.load_feedback()
    elif allow_missing and sample.exists():
        say("no NETLIFY_API_TOKEN: using FAKE sample ratings from data/feedback_sample.json")
        rows = fb.load_feedback(path=str(sample))
    else:
        say("no NETLIFY_API_TOKEN: building without ratings")
    summary = fb.summarize(rows, sentiment)
    return summary, fb.training_rows(rows)


def _empty_summary() -> dict:
    return {"total": 0, "items": [], "by_week": [], "format_rank": {},
            "flagged": [], "sentiment": None}


# ---------- tags, topics, answers ----------
def _answer_text(a: dict) -> str:
    parts = [a["title"], a["summary"]] + [s["label"] + ". " + s["detail"] for s in a["see_it"]["steps"]]
    return " ".join(parts)


def _step_text(s: dict) -> str:
    return f"{s['idea']} {s.get('example', '')}"


def add_tags(answers: list[dict], lessons: list[dict], sf, nlp) -> None:
    """Fill spaCy tags (union with hand-written tags). Without spaCy, keep the hand-written ones."""
    if sf is None:
        return
    a_docs = sf.analyze([_answer_text(a) for a in answers], nlp)
    for a, d in zip(answers, a_docs):
        a["tags"] = sorted(set(a.get("tags", [])) | set(d["tags"]))[:12]
    for les in lessons:
        res = sf.analyze([_step_text(s) for s in les["steps"]], nlp)
        for s, d in zip(les["steps"], res):
            s["tags"] = sorted(set(s.get("tags", [])) | set(d["tags"]))[:8]
        les["tags"] = [t for t, _ in Counter(t for s in les["steps"] for t in s["tags"]).most_common(8)]


def make_topics(answers: list[dict], lessons: list[dict]) -> dict:
    items, index = [], {c: [] for c in CATEGORY_IDS}
    for a in answers:
        tid = f"answer:{a['category']}"
        items.append({"id": tid, "kind": "answer", "category": a["category"], "tags": a.get("tags", [])})
        index[a["category"]].append(tid)
    for les in lessons:
        for s in les["steps"]:
            tid = f"lesson:{les['category']}:{s['n']}"
            items.append({"id": tid, "kind": "lesson", "category": les["category"], "tags": s.get("tags", [])})
            index[les["category"]].append(tid)
    return {"items": items, "index": index}


def rank_answers(answers: list[dict], summary: dict) -> None:
    ranks = (summary or {}).get("format_rank") or {}
    for a in answers:
        r = ranks.get(a["category"])
        a["format_rank"] = list(r) if r and sorted(r) == sorted(FORMATS) else list(FORMATS)


# ---------- stats and metrics ----------
def make_nltk_stats(texts: list[str], frustrated_rows: list[tuple[str, int]], cats: list[str], nf) -> dict:
    if nf is None:
        return {"n_documents": 0, "items": [], "top_phrases": [], "by_category": {},
                "frustration": None, "note": "NLTK was not available in this build"}
    toks = [nf.lemmas(t) for t in texts]
    by_cat = {}
    for c in CATEGORY_IDS:
        sub = [t for t, y in zip(toks, cats) if y == c]
        by_cat[c] = {"n": len(sub), "top_words": nf.top_words(sub, 10)}
    flagged = sum(1 for t, _ in frustrated_rows if nf.frustration(t)["frustrated"])
    n = len(frustrated_rows)
    return {"n_documents": len(texts), "items": nf.top_words(toks, 25),
            "top_phrases": nf.top_phrases(toks, 20, 3), "by_category": by_cat,
            "frustration": {"n": n, "flagged": flagged, "rate": round(flagged / n, 4) if n else 0.0,
                            "threshold": nf.FRUSTRATION_THRESHOLD}}


def vader_metrics(rows: list[dict], nf) -> dict | None:
    if nf is None or not rows:
        return None
    tp = fp = fn = 0
    fns, fps = [], []
    for r in rows:
        pred, true = nf.frustration(r["text"])["frustrated"], r["frustrated"] == "1"
        if pred and true:
            tp += 1
        elif pred:
            fp += 1
            fps.append(r["text"])
        elif true:
            fn += 1
            fns.append(r["text"])
    p = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * rc / (p + rc) if p + rc else 0.0
    return {"library": "NLTK", "threshold": nf.FRUSTRATION_THRESHOLD, "n": len(rows),
            "precision": round(p, 4), "recall": round(rc, 4), "f1": round(f1, 4),
            "false_negatives": fns[:5], "false_positives": fps[:5]}


def spacy_metrics(gold: list[dict] | None, sf, nlp) -> dict | None:
    if sf is None or not gold:
        return None
    res = sf.analyze([g["text"] for g in gold], nlp)
    tp = fp = fn = 0
    prob_ok = prob_n = 0
    errors = []
    for g, r in zip(gold, res):
        exp = {(e["text"].lower(), e["label"]) for e in g.get("entities", [])}
        got = {(e["text"].lower(), e["label"]) for e in r["entities"]
               if e["label"] in ("DEVICE", "APP", "OS", "ERROR_CODE")}
        tp += len(exp & got)
        fp += len(got - exp)
        fn += len(exp - got)
        if exp != got and len(errors) < 5:
            errors.append({"text": g["text"], "expected": sorted(map(list, exp)), "got": sorted(map(list, got))})
        if g.get("problems"):
            prob_n += 1
            gp = {(p["thing"], p["problem"]) for p in g["problems"]}
            rp = {(p["thing"], p["problem"]) for p in r["problems"]}
            prob_ok += bool(gp & rp)
    p = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return {"library": "spaCy", "n": len(gold), "entity_precision": round(p, 4),
            "entity_recall": round(rc, 4),
            "problem_accuracy": round(prob_ok / prob_n, 4) if prob_n else None, "errors": errors}


def write_classifier_report(path: Path, m: dict, tok: str) -> None:
    lines = ["# Classifier report (Neural network)", "",
             f"Tokenizer: `{tok}`" + ("  (local test run, NOT the Netlify model)" if tok == "simple_v1" else ""),
             f"Test set: {m['test_set']}", f"Train rows: {m['n_train']}  Test rows: {m['n_test']}",
             f"Accuracy: {m['accuracy']:.3f}  Macro F1: {m['macro_f1']:.3f}", "",
             "| Category | Precision | Recall | F1 | Support |", "|---|---|---|---|---|"]
    for c, v in m["per_class"].items():
        lines.append(f"| {c} | {v['precision']:.2f} | {v['recall']:.2f} | {v['f1']:.2f} | {v['support']} |")
    lines += ["", "## Mistakes (up to 5)"]
    for e in m["misclassified"]:
        lines.append(f"- \"{e['text']}\": true {e['true']}, predicted {e['pred']} ({e['confidence']:.2f})")
    if not m["misclassified"]:
        lines.append("- none")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------- main ----------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build HelpMate static files")
    ap.add_argument("--out", default="site")
    ap.add_argument("--allow-missing", action="store_true",
                    help="local tests only: skip NLTK/spaCy and use the simple tokenizer")
    args = ap.parse_args(argv)
    on_netlify = os.environ.get("NETLIFY") == "true"
    if args.allow_missing and on_netlify:
        print("[build] ERROR: --allow-missing is not allowed on Netlify", file=sys.stderr)
        return 1
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    try:
        return run(out, args.allow_missing, on_netlify)
    except BuildError as e:
        print(f"[build] ERROR: {e}", file=sys.stderr)
        return 1


def run(out: Path, allow_missing: bool, on_netlify: bool) -> int:
    from nlp import classifier
    data = out / "data"
    skipped: list[str] = []

    say("1/7 checking data/content")
    answers_src = load_json(ROOT / "data/content/answers.json")
    lessons_src = load_json(ROOT / "data/content/lessons.json")
    validate_content(answers_src, lessons_src)
    answers, lessons = answers_src["items"], lessons_src["items"]

    say("2/7 NLTK data")
    nltk_ok = setup_nltk(out, allow_missing)
    nf = None
    if nltk_ok:
        from nlp import nltk_features as nf
        nltk_items = copy_browser_nltk(out)
    else:
        skipped.append("NLTK")
        nltk_items = []

    say("3/7 ratings")
    summary, fb_rows = get_feedback(nltk_ok, allow_missing)

    say("4/7 training the neural network")
    seed = read_seed()
    tok = "nltk_clean_v1" if nltk_ok else "simple_v1"
    if tok == "simple_v1":
        if on_netlify:
            raise BuildError("refusing to publish the simple_v1 tokenizer on Netlify")
        skipped.append("tokenizer (simple_v1 used)")
    tickets = read_tickets()
    tr = [r for r in seed if r["split"] == "train"]
    te = [r for r in seed if r["split"] == "test"]
    if not tr or not te:
        raise BuildError("seed_questions.csv needs rows with split=train and split=test")
    texts = [r["text"] for r in tr] + [t for t, _ in tickets] + [q for q, _ in fb_rows]
    labels = [r["category"] for r in tr] + [c for _, c in tickets] + [c for _, c in fb_rows]
    vec, clf, cmetrics = classifier.train(texts, labels, [r["text"] for r in te],
                                          [r["category"] for r in te], tokenizer=tok)
    model = classifier.export_json(vec, clf, str(data / "model.json"), tokenizer=tok,
                                   extra={"trained_on": {"n_train": len(texts), "n_feedback": len(fb_rows)}})

    say("5/7 spaCy")
    sf, nlp = setup_spacy(allow_missing)
    if sf is None:
        skipped.append("spaCy")
    add_tags(answers, lessons, sf, nlp)
    rank_answers(answers, summary)
    write_json(data / "topics.json", make_topics(answers, lessons), "spaCy")
    write_json(data / "answers.json", {"items": answers}, "NLTK + spaCy")
    write_json(data / "lessons.json", {"items": lessons}, "spaCy")
    # export_patterns needs no spaCy install, so the browser always gets the IT vocabulary
    import nlp.spacy_features as sf_export
    sf_export.export_patterns(str(data / "entity_patterns.json"),
                              str(ROOT / "nlp/patterns/it_entities.jsonl"),
                              str(ROOT / "nlp/patterns/category_hints.json"))
    write_json(data / "ratings_summary.json", summary, "NLTK")

    # examples: 2 per category from the test split
    ex_rows = []
    for c in CATEGORY_IDS:
        ex_rows += [r for r in te if r["category"] == c][:2]
    analyzed = sf.analyze([r["text"] for r in ex_rows], nlp) if sf else [None] * len(ex_rows)
    examples = []
    for r, an in zip(ex_rows, analyzed):
        pred = classifier.predict_numpy(model, r["text"])
        mood = None
        if nf:
            fr = nf.frustration(r["text"])
            mood = {"compound": round(fr["compound"], 4), "frustrated": fr["frustrated"],
                    "reasons": fr["reasons"]}
        examples.append({"id": r["id"], "text": r["text"], "category": pred["category"],
                         "confidence": round(pred["confidence"], 4), "mood": mood,
                         "entities": an["entities"] if an else [], "problems": an["problems"] if an else []})
    write_json(data / "examples.json", {"items": examples}, "NLTK + spaCy")

    say("6/7 statistics and metrics")
    all_texts = [r["text"] for r in tr] + [t for t, _ in tickets] + [q for q, _ in fb_rows]
    stats = make_nltk_stats(all_texts, [(r["text"], int(r["frustrated"])) for r in seed], labels, nf)
    write_json(data / "nltk_stats.json", stats, "NLTK")
    metrics = {"items": [], "classifier": cmetrics, "vader": vader_metrics(seed, nf),
               "spacy": spacy_metrics(read_gold(), sf, nlp)}
    write_json(data / "metrics.json", metrics, "Neural network")
    write_classifier_report(ROOT / "reports" / "classifier.md", cmetrics, tok)

    say("7/7 copying files for the browser")
    py_root = out / "py"
    if (py_root / "nlp").exists():
        shutil.rmtree(py_root / "nlp")
    for rel in PY_FILES:
        (py_root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, py_root / rel)
    brand = ROOT / "assets" / "brand"
    if brand.exists():
        shutil.copytree(brand, out / "assets" / "brand", dirs_exist_ok=True)
    nbytes = sum(p.stat().st_size for p in (out / "nltk_data").rglob("*") if p.is_file()) \
        if (out / "nltk_data").exists() else 0
    nbytes += sum((ROOT / rel).stat().st_size for rel in PY_FILES)
    version = None
    if nltk_ok:
        import nltk
        version = nltk.__version__
    write_json(data / "nltk_manifest.json",
               {"base_url": "nltk_data/", "fs_root": "/nltk_data", "items": nltk_items,
                "python_base_url": "py/", "python_files": PY_FILES, "bytes": nbytes,
                "nltk_version": version or NLTK_VERSION_PIN}, "NLTK")

    print("\n[build] Summary")
    for p in sorted(data.glob("*.json")):
        print(f"  {p.relative_to(out)}  {p.stat().st_size:,} bytes")
    print(f"  tokenizer={tok}  accuracy={cmetrics['accuracy']:.3f}  n_train={len(texts)}  "
          f"n_feedback={len(fb_rows)}  ratings={summary.get('total', 0)}")
    if skipped:
        print(f"  SKIPPED: {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
