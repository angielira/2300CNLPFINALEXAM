---
name: model-export-json
description: "Export the trained TF-IDF + MLP to JSON and run it with NumPy in the browser. Use after training or when wiring the live box."
---

# model-export-json

Used by: ml-engineer, pyodide-engineer

## Export
```python
model = {
  "vocabulary": {t: int(i) for t, i in vec.vocabulary_.items()},
  "idf": vec.idf_.tolist(), "ngram_range": list(vec.ngram_range), "sublinear_tf": vec.sublinear_tf,
  "coefs": [w.tolist() for w in clf.coefs_], "intercepts": [b.tolist() for b in clf.intercepts_],
  "classes": clf.classes_.tolist(), "activation": clf.activation,
}
```
## Predict (NumPy only)
1. Build the n-gram counts with the same lowercase/tokenization; tf (1+log if sublinear) x idf; L2-normalize.
2. `h = relu(x @ W0 + b0)`; `z = h @ W1 + b1`; softmax -> probabilities.
- Test: NumPy predictions must equal `clf.predict` on the test set.
- Why not pickle: pickles need the same scikit-learn version and can execute code on load.
