"""Compare classifier settings with repeated 5-fold CV on the seed TRAIN split only.

The test split is never used here, so this is safe for choosing settings.
Usage (repo root):
    python pipeline/eval_classifier.py                      # simple_v1 (works without NLTK)
    python pipeline/eval_classifier.py --tokenizer nltk_clean_v1   # needs nltk + .cache/nltk_data
Owner: nlp-evaluator. Results go in reports/nlp_quality.md.
"""
from __future__ import annotations

import argparse
import csv
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONFIGS = {
    "old: (1,2) alpha 1e-3": {"ngram_range": (1, 2), "alpha": 1e-3},
    "(1,2) alpha 1e-2": {"ngram_range": (1, 2), "alpha": 1e-2},
    "(1,1) alpha 1e-3": {"ngram_range": (1, 1), "alpha": 1e-3},
    "new: (1,1) alpha 1e-2": {"ngram_range": (1, 1), "alpha": 1e-2},
    "(1,1) alpha 1e-1": {"ngram_range": (1, 1), "alpha": 1e-1},
}


def main(argv=None) -> int:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import RepeatedStratifiedKFold
    from sklearn.neural_network import MLPClassifier

    from nlp import classifier

    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", default="simple_v1")
    ap.add_argument("--repeats", type=int, default=5)
    args = ap.parse_args(argv)
    if args.tokenizer == "nltk_clean_v1":
        from nlp import nltk_features
        nltk_features.use_data_dir(str(ROOT / ".cache" / "nltk_data"))
    tok = classifier.get_tokenizer(args.tokenizer)

    with open(ROOT / "data" / "seed_questions.csv", encoding="utf-8", newline="") as f:
        tr = [r for r in csv.DictReader(f) if r["split"] == "train"]
    X = np.array([r["text"] for r in tr])
    y = np.array([r["category"] for r in tr])
    splits = list(RepeatedStratifiedKFold(n_splits=5, n_repeats=args.repeats, random_state=1).split(X, y))

    warnings.filterwarnings("ignore")
    res = {}
    for name, cfg in CONFIGS.items():
        accs, conf = [], []
        for i, (a, b) in enumerate(splits):
            vec = TfidfVectorizer(tokenizer=tok, lowercase=False, token_pattern=None, ngram_range=cfg["ngram_range"],
                                  max_features=2000, min_df=1, sublinear_tf=True, norm="l2", smooth_idf=True)
            clf = MLPClassifier(hidden_layer_sizes=(64,), solver="lbfgs", alpha=cfg["alpha"], max_iter=500,
                                random_state=i)
            clf.fit(vec.fit_transform(X[a]), y[a])
            p = clf.predict_proba(vec.transform(X[b]))
            accs.append(accuracy_score(y[b], clf.classes_[p.argmax(1)]))
            conf += list(p.max(1))
        res[name] = (np.array(accs), np.array(conf))
    base = res["old: (1,2) alpha 1e-3"][0]
    print(f"tokenizer={args.tokenizer}  train rows={len(tr)}  folds={len(splits)}")
    for name, (accs, conf) in res.items():
        d = accs - base
        print(f"{name:24s} cv_acc={accs.mean():.3f}  vs old {d.mean():+.3f} (paired se {d.std(ddof=1) / np.sqrt(len(d)):.3f},"
              f" better/worse folds {int((d > 0).sum())}/{int((d < 0).sum())})"
              f"  unsure@{classifier.DEFAULT_MIN_CONFIDENCE}={float((conf < classifier.DEFAULT_MIN_CONFIDENCE).mean()):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
