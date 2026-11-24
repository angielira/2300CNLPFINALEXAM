# 0004. Export the MLP classifier as JSON and run it with NumPy
Date: 2026-11-23
Status: accepted

## Context
- The neural network is trained at build time with scikit-learn (`nlp/classifier.py`: `TfidfVectorizer` + `MLPClassifier(hidden_layer_sizes=(64,), solver="lbfgs")`).
- It must predict in the browser (ADR 0003). Pyodide ships scikit-learn, but a pickle only loads reliably with the same scikit-learn version, and the build pins `scikit-learn==1.9.1`, while Pyodide 314.0.8 ships 1.8.0 (docs/04-neural-network.md). The scikit-learn wheel also adds several MB to the first load.
- A one-hidden-layer MLP is two matrix multiplications.

## Decision
We will export the fitted vectorizer and network to `site/data/model.json` with `classifier.export_json`, written with
`compact=True`: `vocabulary` as a list (position = feature column), `idf`, `ngram_range`, `sublinear_tf`, `norm`,
`activation`, `coefs`, `intercepts`, `classes`, `min_confidence` (0.45), `tokenizer` and `trained_on`.
We will predict with `classifier.predict_numpy`, which rebuilds the TF-IDF vector (same tokenizer, n-grams,
`1 + ln(count)`, l2 norm), then ReLU hidden layer, softmax output, and marks `unsure` when no term is known or confidence is below `min_confidence`.
`nlp/classifier.py` imports only json, math, re, collections and numpy at top level (scikit-learn inside functions), so the same file runs in Pyodide.

## Consequences
- Positive: no scikit-learn in the browser, no pickle version lock, no unsafe pickle loading; the build may use any scikit-learn version.
- Positive: the shipped model is the one the metrics describe (trained on the train split, tested on the seed test split).
- Positive: size is small. With the as-built settings (`NGRAM_RANGE = (1, 1)`, `MLP_ALPHA = 1e-2`, see `reports/plan.md` "As built") `model.json` is about 450 KB, under the 2 MB limit.
- Negative: `predict_numpy` must stay exactly in step with scikit-learn's vectorizer and MLP. Guarded by `tests/test_classifier.py` (matches `predict_proba` and argmax).
- Negative: token parity depends on the same `nltk` version in the build and in Pyodide. The build warns if `nltk` is not 3.9.4 and refuses to publish the `simple_v1` test tokenizer on Netlify.
- Follow-up: ml-engineer to re-run `python pipeline/eval_classifier.py --tokenizer nltk_clean_v1` where NLTK is installed (the n-gram choice was made with `simple_v1`).

## Alternatives considered
- **Pickle and load scikit-learn in Pyodide:** version lock and a bigger first load. Rejected.
- **ONNX or TensorFlow.js:** extra runtime and converter for a 64-unit network. Rejected as heavier than needed.
- **Rewrite inference in JavaScript:** possible, but the result would no longer come from the same Python code that is tested at build time.
