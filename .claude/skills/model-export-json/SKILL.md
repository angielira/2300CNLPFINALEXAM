---
name: model-export-json
description: "Export the trained TF-IDF + MLP to site/data/model.json (vocabulary as a list) and run it with NumPy in the browser. Use after training or when wiring the live box."
---

# model-export-json

Used by: ml-engineer, pyodide-engineer

Binding contract: `reports/plan.md` sections 3 (model.json) and 4.3. If anything here differs from the plan, the plan wins.

## Export (`nlp/classifier.export_json(vec, clf, path, tokenizer="nltk_clean_v1", extra=None) -> dict`)
```python
from nlp.common import write_json

def _r(x):                                   # 6 significant digits
    return float(f"{x:.6g}")

inv = {int(i): t for t, i in vec.vocabulary_.items()}
vocabulary = [inv[i] for i in range(len(inv))]     # list: position = feature column

payload = {
  "tokenizer": tokenizer,                    # "nltk_clean_v1" (shipped) or "simple_v1" (local tests only)
  "tokenizer_note": "nlp.nltk_features.clean: lower, RegexpTokenizer, stopwords minus negations, PorterStemmer",
  "vocabulary": vocabulary,
  "idf": [_r(v) for v in vec.idf_],          # same order as vocabulary
  "ngram_range": list(vec.ngram_range), "sublinear_tf": bool(vec.sublinear_tf), "norm": vec.norm,
  "activation": clf.activation, "out_activation": clf.out_activation_,
  "hidden_layer_sizes": list(clf.hidden_layer_sizes),
  "coefs": [[[_r(v) for v in row] for row in w] for w in clf.coefs_],
  "intercepts": [[_r(v) for v in b] for b in clf.intercepts_],
  "classes": clf.classes_.tolist(),          # alphabetical, as sklearn stores them
  "min_confidence": 0.45, "trained_on": {"n_train": 0, "n_feedback": 0}, "items": [],
}
payload.update(extra or {})                  # e.g. real trained_on counts
write_json(path, payload, "Neural network", compact=True)
```
- `vocabulary` is a **list**, never a dict. Inverting `vec.vocabulary_` gives the same order as `vec.get_feature_names_out()`.
- `coefs[0]` has one row per vocabulary term (64 floats each); `coefs[1]` has 64 rows of 8 floats.
- Size limit: < 2 MB raw (Netlify compresses it). If it goes over, cut `max_features` to 1500.

## Predict (`predict_numpy(model, text) -> dict`, NumPy only)
1. `toks = get_tokenizer(model["tokenizer"])(text)`.
2. Grams: for n in `ngram_range[0]..ngram_range[1]`, `" ".join(toks[i:i+n])` for every i (matches sklearn's `_word_ngrams`).
3. Build `{term: column}` from `vocabulary` once. Count known grams; `tf = 1 + ln(count)` if `sublinear_tf`, else count.
4. `x[col] = tf * idf[col]`; if norm is l2 and `||x|| > 0`, divide by `||x||`.
5. `h = relu(x @ W0 + b0)` (also support tanh, logistic, identity); `z = h @ W1 + b1`; softmax with max subtraction.
6. Return `{"category", "confidence", "probabilities": {cls: p}, "known_terms", "unsure", "library": "Neural network"}` with `unsure = known_terms == 0 or confidence < model["min_confidence"]`.

## Checks
- Test: `predict_numpy` matches `clf.predict_proba` (atol 1e-4 after rounding) and the argmax on every test row.
- `pipeline/build.py` refuses to publish `tokenizer == "simple_v1"` when `NETLIFY == "true"`.
- Why not pickle: pickles need the same scikit-learn version and can execute code on load.
