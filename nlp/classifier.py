"""HelpMate question classifier: TF-IDF + MLP, exported to JSON, predicted with NumPy.

Top-level imports are json, math, re, collections and numpy only, so this file
also imports in Pyodide. scikit-learn and nlp.common are imported inside functions.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter  # noqa: F401  (kept for the plan's import list)

import numpy as np

TOKEN_PATTERN = r"[a-z0-9]+(?:'[a-z]+)?"

# Local tests only. The shipped model uses "nltk_clean_v1".
SIMPLE_STOP = frozenset(
    "a an the and or but if of to in on at for with from by as is are was were be been am "
    "i my me we our you your it its this that these those so do does did".split()
)

DEFAULT_MIN_CONFIDENCE = 0.45

# Chosen by 5x5-fold CV on the seed TRAIN split only (simple_v1, reports/nlp_quality.md):
# unigrams + alpha 1e-2 gave CV accuracy 0.780 vs 0.729 for (1, 2) + alpha 1e-3, and kept the
# "unsure" rate at min_confidence 0.45 about the same (14% vs 12%). Re-check with nltk_clean_v1.
NGRAM_RANGE = (1, 1)
MLP_ALPHA = 1e-2


def simple_clean(text: str) -> list[str]:
    toks = re.findall(TOKEN_PATTERN, text.replace("’", "'").lower())
    return [t for t in toks if t not in SIMPLE_STOP]


def get_tokenizer(name: str):
    if name == "nltk_clean_v1":
        from nlp.nltk_features import clean  # lazy: needs nltk

        return clean
    if name == "simple_v1":
        return simple_clean
    raise ValueError(f"unknown tokenizer {name!r}")


def _r(x) -> float:
    return float(f"{x:.6g}")


def train(texts, labels, test_texts=None, test_labels=None, tokenizer: str = "nltk_clean_v1"):
    """Fit on train rows. Returns (vec, clf, metrics) where metrics matches metrics.json['classifier']."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    from sklearn.model_selection import train_test_split
    from sklearn.neural_network import MLPClassifier

    from nlp.common import CATEGORY_IDS

    texts, labels = list(texts), list(labels)
    if test_texts is None:
        texts, test_texts, labels, test_labels = train_test_split(
            texts, labels, test_size=0.2, stratify=labels, random_state=42
        )
        test_name = "seed questions, stratified 20% split"
    else:
        test_texts, test_labels = list(test_texts), list(test_labels)
        test_name = "seed questions, split=test"

    vec = TfidfVectorizer(
        tokenizer=get_tokenizer(tokenizer), lowercase=False, token_pattern=None,
        preprocessor=None, stop_words=None, ngram_range=NGRAM_RANGE, max_features=2000,
        min_df=1, sublinear_tf=True, norm="l2", smooth_idf=True,
    )
    X = vec.fit_transform(texts)
    clf = MLPClassifier(hidden_layer_sizes=(64,), solver="lbfgs", alpha=MLP_ALPHA,
                        max_iter=500, random_state=42)
    clf.fit(X, labels)

    proba = clf.predict_proba(vec.transform(test_texts))
    pred = clf.classes_[proba.argmax(axis=1)]
    labs = [c for c in CATEGORY_IDS if c in set(clf.classes_) or c in set(test_labels)]
    p, r, f, s = precision_recall_fscore_support(test_labels, pred, labels=labs, zero_division=0)
    idx = {c: i for i, c in enumerate(labs)}
    matrix = [[0] * len(labs) for _ in labs]
    for t, q in zip(test_labels, pred):
        matrix[idx[t]][idx[q]] += 1
    miss = [
        {"text": t, "true": y, "pred": str(q), "confidence": _r(float(pr.max()))}
        for t, y, q, pr in zip(test_texts, test_labels, pred, proba) if y != q
    ][:5]
    metrics = {
        "library": "Neural network", "tokenizer": tokenizer, "test_set": test_name,
        "n_train": len(texts), "n_test": len(test_texts),
        "accuracy": _r(accuracy_score(test_labels, pred)),
        "macro_f1": _r(float(np.mean(f))),
        "macro_precision": _r(float(np.mean(p))), "macro_recall": _r(float(np.mean(r))),
        "per_class": {c: {"precision": _r(p[i]), "recall": _r(r[i]), "f1": _r(f[i]), "support": int(s[i])}
                      for c, i in idx.items()},
        "confusion_matrix": {"labels": labs, "matrix": matrix},
        "misclassified": miss,
    }
    return vec, clf, metrics


def export_json(vec, clf, path: str, tokenizer: str = "nltk_clean_v1", extra: dict | None = None) -> dict:
    """Write model.json (compact, 6 significant digits). Returns the payload."""
    from nlp.common import write_json

    inv = {int(i): t for t, i in vec.vocabulary_.items()}
    payload = {
        "tokenizer": tokenizer,
        "tokenizer_note": "nlp.nltk_features.clean: lower, RegexpTokenizer, stopwords minus negations, PorterStemmer"
        if tokenizer == "nltk_clean_v1" else "nlp.classifier.simple_clean: local tests only",
        "vocabulary": [inv[i] for i in range(len(inv))],
        "idf": [_r(v) for v in vec.idf_],
        "ngram_range": list(vec.ngram_range), "sublinear_tf": bool(vec.sublinear_tf), "norm": vec.norm,
        "activation": clf.activation, "out_activation": clf.out_activation_,
        "hidden_layer_sizes": [int(h) for h in clf.hidden_layer_sizes],
        "coefs": [[[_r(v) for v in row] for row in w] for w in clf.coefs_],
        "intercepts": [[_r(v) for v in b] for b in clf.intercepts_],
        "classes": [str(c) for c in clf.classes_],
        "min_confidence": DEFAULT_MIN_CONFIDENCE,
        "trained_on": {"n_train": 0, "n_feedback": 0}, "items": [],
    }
    payload.update(extra or {})
    write_json(path, payload, "Neural network", compact=True)
    return payload


_COLS_CACHE: dict = {}


def _activate(name: str, z):
    if name == "relu":
        return np.maximum(z, 0.0)
    if name == "tanh":
        return np.tanh(z)
    if name == "logistic":
        return 1.0 / (1.0 + np.exp(-z))
    if name == "identity":
        return z
    raise ValueError(f"unsupported activation {name!r}")


def predict_numpy(model: dict, text: str) -> dict:
    toks = get_tokenizer(model["tokenizer"])(text)
    lo, hi = model["ngram_range"]
    grams = [" ".join(toks[i:i + n]) for n in range(lo, hi + 1) for i in range(len(toks) - n + 1)]
    vocab = model["vocabulary"]
    hit = _COLS_CACHE.get(id(vocab))
    if hit is None or hit[0] is not vocab:
        hit = (vocab, {t: i for i, t in enumerate(vocab)})
        _COLS_CACHE.clear()
        _COLS_CACHE[id(vocab)] = hit
    cols = hit[1]
    counts: dict[int, int] = {}
    for g in grams:
        c = cols.get(g)
        if c is not None:
            counts[c] = counts.get(c, 0) + 1
    idf = model["idf"]
    x = np.zeros(len(model["vocabulary"]))
    for c, n in counts.items():
        tf = 1.0 + math.log(n) if model["sublinear_tf"] else float(n)
        x[c] = tf * idf[c]
    if model["norm"] == "l2":
        nrm = float(np.linalg.norm(x))
        if nrm > 0:
            x = x / nrm
    W = [np.asarray(w, dtype=float) for w in model["coefs"]]
    b = [np.asarray(v, dtype=float) for v in model["intercepts"]]
    h = x
    for k in range(len(W) - 1):
        h = _activate(model["activation"], h @ W[k] + b[k])
    z = h @ W[-1] + b[-1]
    if model["out_activation"] == "logistic":
        p = 1.0 / (1.0 + np.exp(-z))
        p = p / p.sum()
    else:
        e = np.exp(z - z.max())
        p = e / e.sum()
    best = int(p.argmax())
    conf = float(p[best])
    known = len(counts)
    return {
        "category": model["classes"][best], "confidence": conf,
        "probabilities": {c: float(v) for c, v in zip(model["classes"], p)},
        "known_terms": known,
        "unsure": known == 0 or conf < model.get("min_confidence", DEFAULT_MIN_CONFIDENCE),
        "library": "Neural network",
    }
