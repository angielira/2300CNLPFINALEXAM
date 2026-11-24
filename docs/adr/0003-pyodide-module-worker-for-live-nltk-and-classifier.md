# 0003. Run NLTK and the classifier live in a Pyodide module Web Worker
Date: 2026-11-23
Status: accepted

## Context
- The live "Ask HelpMate" box must clean the question with NLTK, score frustration with VADER and run the classifier, with no server (ADR 0001).
- Pyodide (Python compiled to WebAssembly) includes `nltk` and `numpy` (docs/06-netlify-architecture.md, docs/04-neural-network.md).
- Loading Pyodide takes seconds and its Python calls block the thread they run on; the page must stay responsive for non-technical users.
- The same Python code must give the same tokens in the build and in the browser, so `requirements.txt` pins `nltk==3.9.4` to match Pyodide 314.0.8.
- **Live-site finding:** the first worker was a classic worker that called `importScripts` on Pyodide's `pyodide.js`. On the deployed site the browser refused it: `importScripts` threw a `NetworkError` ("failed to load", as recorded in the comment at the top of `site/js/brain-worker.js`), so the live box never started and the app fell back to spaCy category hints.

## Decision
We will run Pyodide in a **module** Web Worker. `site/js/brain.js` creates it with
`new Worker(new URL("./brain-worker.js", import.meta.url), { type: "module" })`, and `site/js/brain-worker.js` imports
Pyodide's ES-module build with a pinned URL:
`import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs"`.
The worker then:
1. calls `loadPackage(["nltk", "numpy"])` while it fetches `data/nltk_manifest.json` and `data/model.json`;
2. writes the manifest's `python_files` into `/py/` and its NLTK `items` into `/nltk_data` in Pyodide's file system (no `nltk.download()` in the browser);
3. runs the `PY_GLUE` Python (between `PY_GLUE_START`/`PY_GLUE_END`, tested by `tests/test_brain_python_path.py`), which calls `classifier.predict_numpy` and `nltk_features.frustration`;
4. does one warm-up call so data problems show at start-up.

`brain.js` exposes `ready()`, `analyze(text)` and `onProgress(fn)`, uses a 110 s load timeout and a 15 s answer timeout,
and rejects with a plain-language message on failure. `app.js` imports `brain.js` lazily and falls back to the spaCy
`category_hint` (badged spaCy) when it rejects. Results are labelled "Neural network + NLTK", or "Neural network" if VADER failed.

## Consequences
- Positive: the main thread never blocks; progress messages ("Starting the Python engine...") keep users informed.
- Positive: ES-module import of `pyodide.mjs` works on the live site where `importScripts` did not.
- Positive: one pinned Pyodide version; the same `nlp/*.py` files run in the build and the browser.
- Negative: module workers need a modern browser (older Firefox and Safari versions lack them). Those users get the spaCy fallback, not an error page.
- Negative: first visit downloads Pyodide, NLTK and NumPy from jsDelivr (several MB). A jsDelivr outage disables the live box; the fallback still works. No Subresource Integrity is possible on a dynamic module import here, so trust rests on the pinned version path.
- Negative: no CSP can be strict while Pyodide needs `wasm-unsafe-eval` (see ADR 0001).
- Follow-up: qa-engineer to confirm on the live site that Pyodide reports nltk 3.9.4 (token parity, plan risk 3).

## Alternatives considered
- **Classic worker with `importScripts(".../pyodide.js")`:** what we shipped first; failed on the live site with a NetworkError. Replaced.
- **Pyodide on the main thread:** simpler, but freezes the page during load and every call. Rejected.
- **Rewrite the cleaning and VADER in JavaScript:** no Pyodide download, but two implementations to keep in step and NLTK would no longer be the library that made the result. Rejected.
- **Self-host Pyodide files in `site/`:** removes the CDN dependency but adds tens of MB to every deploy. Not now; revisit if jsDelivr is unreliable.
