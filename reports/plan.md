# HelpMate build plan and file contracts (Atlas, 2026-11-22)

Sources: CLAUDE.md, docs/README.md, docs/expert-roster.md, docs/04-neural-network.md, docs/06-netlify-architecture.md,
the skills in `.claude/skills/`. Contracts below are binding: an expert who needs to change one must ask Atlas first.

## 0. Ground rules
- Python runs only at Netlify build time. In the browser, only Pyodide (nltk + numpy) and JavaScript run. spaCy never runs in the browser. No backend server, no database.
- **This workspace:** Python 3.13, scikit-learn 1.9.1, numpy 2.5.3, pytest, playwright are installed. **nltk and spacy are NOT installed and there is no network.** Write NLTK/spaCy code from the docs so it is correct without running it here. Netlify runs it (Python 3.12).
- Tests that need nltk or spacy start with `pytest.importorskip("nltk")` / `pytest.importorskip("spacy")`. They also skip on `LookupError` (missing NLTK data) or `OSError` (missing spaCy model).
- Every user-facing result carries a library badge (section 7). Never commit secrets, `.env` or build outputs.

## 1. Directory layout
```
data/                      (source data, committed)
  seed_questions.csv       id,text,category,frustrated,source,split      (dataset-curator)
  tickets_sample.csv       id,text,category,source,orig_queue,orig_tags  (dataset-curator; optional, see risks)
  spacy_gold.jsonl         gold entities + problems for evaluation        (dataset-curator)
  feedback_sample.json     fake Netlify submissions for tests, no PII     (feedback-loop-engineer)
  fetch_tickets.py         one-off sampler, run by hand where network exists (dataset-curator)
  README.md                sources, licenses, creators, DOI, date accessed  (dataset-curator)
  content/answers.json     hand-written answers, no generated_at          (instructional-designer)
  content/lessons.json     hand-written 10-step courses                   (instructional-designer)
nlp/
  __init__.py  common.py  nltk_features.py  spacy_features.py  classifier.py
  patterns/it_entities.jsonl     spaCy EntityRuler patterns (source of truth)
  patterns/category_hints.json   {"<entity id>": "<category id>"}
pipeline/
  __init__.py  build.py  feedback.py
site/                      (publish folder)
  index.html  insights.html
  css/tokens.css  css/helpmate.css  css/insights.css
  js/app.js  js/formats.js  js/speech.js  js/progress.js  js/rating.js  js/entities.js   (frontend-engineer)
  js/brain.js  js/brain-worker.js                                               (pyodide-engineer)
  js/insights.js  js/charts.js                                                  (data-viz-expert)
  assets/brand/helpmate-mark.svg  assets/brand/favicon.svg  assets/steps/*.svg (optional)
  data/        BUILD OUTPUT (gitignored): the JSON files of section 3
  nltk_data/   BUILD OUTPUT (gitignored): NLTK files listed in nltk_manifest.json
  py/nlp/      BUILD OUTPUT (gitignored): __init__.py, nltk_features.py, classifier.py copied for Pyodide
netlify/functions/rebuild.mjs   optional scheduled rebuild (JS)               (netlify-engineer)
tests/  test_common.py test_nltk_features.py test_spacy_features.py test_classifier.py
        test_feedback.py test_build.py test_site_json.py  fixtures/site_data/*.json  browser/test_app.py
reports/  plan.md  quality.md  classifier.md  figures/*.svg
netlify.toml  requirements.txt  requirements-dev.txt  .gitignore  README.md
```
`.gitignore`: `site/data/`, `site/nltk_data/`, `site/py/`, `.cache/`, `__pycache__/`, `.env`, `.venv/`.

## 2. Categories and formats (`nlp/common.py`, stdlib only)
| id | display name |
|---|---|
| printer | Printer |
| email | Email |
| wifi | Wi-Fi & Internet |
| passwords | Passwords & Login |
| slow | Slow computer |
| phone_apps | Phone & Apps |
| files | Files & Storage |
| video_calls | Video calls |

```python
CATEGORIES: list[tuple[str, str]] = [("printer", "Printer"), ...]   # order above; this order everywhere
CATEGORY_IDS: list[str]; DISPLAY_NAMES: dict[str, str]
FORMATS = ["see_it", "hear_it", "try_it", "read_it"]   # See it, Hear it, Try it, Read it
LIBRARIES = ("NLTK", "spaCy", "Neural network", "NLTK + spaCy")
SCHEMA_VERSION = 1
def utc_now() -> str            # "2026-11-22T10:00:00Z"
def write_json(path, payload: dict, library: str, compact: bool = False) -> pathlib.Path
    # adds generated_at, library (must be in LIBRARIES), schema_version; mkdir parents;
    # UTF-8, ensure_ascii=False, sort_keys=True; compact -> separators=(",", ":"), else indent=1
```

## 3. `site/data/` JSON contracts
Every file: `{"generated_at": str, "library": <one of LIBRARIES>, "schema_version": 1, "items": [...], ...}`.
Raw size < 1 MB, except model.json < 2 MB (Netlify compresses it). The browser must treat any missing file as "not ready yet" and never crash.

**answers.json** (library `"NLTK + spaCy"`: text by the team, `tags` from spaCy, `format_rank` from NLTK-scored ratings). One item per category, in CATEGORIES order:
```json
{"category": "printer", "title": "Let's get your printer printing", "summary": "Most printer problems are power, paper or connection.",
 "calm_intro": "It's okay. Printers are fussy. We'll fix this together, one small step at a time.",
 "when_to_get_help": "If none of this works, ask someone you trust or the printer maker's help line.",
 "tags": ["printer", "paper", "ink"], "format_rank": ["see_it", "try_it", "hear_it", "read_it"],
 "see_it":  {"steps": [{"n": 1, "label": "Check the power", "detail": "Look for a small light on the printer.", "image": null, "alt": ""}]},
 "hear_it": {"intro": "Here's what we'll do.", "script": ["Step one. Check the printer is switched on."], "outro": "Well done."},
 "try_it":  {"steps": [{"id": "printer-try-1", "text": "The printer light is on."}]},
 "read_it": {"print_title": "Printer checklist", "checklist": ["Printer switched on"]}}
```
Rules: 4-8 steps. `see_it.steps`, `try_it.steps`, `hear_it.script` and `read_it.checklist` have the same length and order. `image` is a path under `assets/steps/` or null. `alt` is required when `image` is set. `format_rank` defaults to FORMATS order.

**lessons.json** (library `"spaCy"`: the tags). One item per category:
```json
{"category": "printer", "title": "Printer basics in 10 steps", "badge": {"id": "printer-pro", "name": "Printer Pro"},
 "tags": ["printer", "queue"],
 "steps": [{"n": 1, "idea": "A printer needs power, paper and a connection.", "example": "Like a toaster needs a plug and bread.",
            "check_question": "What three things does a printer need?",
            "choices": ["Power, paper, connection", "A password", "A new cable every week"], "answer": 0,
            "explain": "Power, paper and a connection are the basics.", "tags": ["printer", "paper"]}]}
```
Rules: exactly 10 steps, `n` = 1..10. 3 choices. `answer` is a 0-based index into `choices`. `explain` is optional.

**entity_patterns.json** (library `"spaCy"`): exported from the EntityRuler for JS matching.
```json
{"labels": ["DEVICE", "APP", "OS", "ERROR_CODE"],
 "items": [{"id": "outlook", "label": "APP", "phrases": ["outlook", "microsoft outlook"], "category_hint": "email"}],
 "regex": [{"label": "ERROR_CODE", "pattern": "\\b0x[0-9a-f]{8}\\b", "flags": "i"}], "skipped_patterns": 0}
```
Phrases are lower-case. JS matches them against the lower-cased question with `(^|[^a-z0-9])PHRASE([^a-z0-9]|$)`, longest phrase first. `category_hint` is a category id or null.

**topics.json** (library `"spaCy"`):
```json
{"items": [{"id": "answer:printer", "kind": "answer", "category": "printer", "tags": ["printer", "ink"]},
           {"id": "lesson:printer:3", "kind": "lesson", "category": "printer", "tags": ["queue"]}],
 "index": {"printer": ["answer:printer", "lesson:printer:3"]}}
```

**nltk_stats.json** (library `"NLTK"`): computed with `lemmas()` over every training question.
```json
{"n_documents": 412, "items": [{"word": "printer", "count": 57}],
 "top_phrases": [{"phrase": "forgot password", "count": 9, "score": 41.2}],
 "by_category": {"printer": {"n": 50, "top_words": [{"word": "print", "count": 30}]}},
 "frustration": {"n": 200, "flagged": 48, "rate": 0.24, "threshold": -0.4}}
```
`items` = top 25 words. `top_phrases` = top 20 by likelihood ratio, min frequency 3. `by_category` = top 10 per category.

**model.json** (library `"Neural network"`, written with `compact=True`, floats rounded with `float(f"{x:.6g}")`):
```json
{"tokenizer": "nltk_clean_v1", "tokenizer_note": "nlp.nltk_features.clean: lower, RegexpTokenizer, stopwords minus negations, PorterStemmer",
 "vocabulary": ["print", "printer", "not print"], "idf": [2.1, 1.7, 3.4], "ngram_range": [1, 2], "sublinear_tf": true,
 "norm": "l2", "activation": "relu", "out_activation": "softmax", "hidden_layer_sizes": [64],
 "coefs": [[[...64 floats] , "...one row per vocabulary term"], [[...8 floats], "...64 rows"]], "intercepts": [[...64], [...8]],
 "classes": ["email", "files", "passwords", "phone_apps", "printer", "slow", "video_calls", "wifi"],
 "min_confidence": 0.45, "trained_on": {"n_train": 330, "n_feedback": 12}, "items": []}
```
`vocabulary` is a list: position = feature column (from `vec.vocabulary_` inverted). `classes` = `clf.classes_` (alphabetical). `tokenizer` is `"nltk_clean_v1"` or `"simple_v1"` (local tests only; see 4.3).

**ratings_summary.json** (library `"NLTK"`): aggregates only, no comment text or question text (privacy).
```json
{"total": 37, "items": [{"category": "printer", "format": "see_it", "count": 6, "avg_stars": 4.2, "avg_compound": 0.31, "score": 0.74}],
 "by_week": [{"week": "2026-W47", "count": 12, "avg_stars": 4.0}],
 "format_rank": {"printer": ["try_it", "see_it", "hear_it", "read_it"]},
 "flagged": [{"category": "wifi", "format": "read_it", "reason": "avg_stars < 2.5 over 3+ ratings"}],
 "sentiment": {"positive": 20, "neutral": 10, "negative": 7}}
```
`score = (5*0.6 + n*raw)/(5 + n)` with `raw = 0.7*(avg_stars-1)/4 + 0.3*(avg_compound+1)/2` (smoothed toward 0.6). An empty feedback list gives `total: 0`, empty lists and default ranks.

**metrics.json** (top level library `"Neural network"`; each section has its own `library`):
```json
{"items": [],
 "classifier": {"library": "Neural network", "tokenizer": "nltk_clean_v1", "test_set": "seed questions, split=test",
   "n_train": 330, "n_test": 40, "accuracy": 0.85, "macro_f1": 0.84,
   "per_class": {"printer": {"precision": 0.9, "recall": 0.8, "f1": 0.85, "support": 5}},
   "confusion_matrix": {"labels": ["printer", "..."], "matrix": [[4, 1]]},
   "misclassified": [{"text": "my email won't send from my phone", "true": "email", "pred": "phone_apps", "confidence": 0.51}]},
 "vader": {"library": "NLTK", "threshold": -0.4, "n": 200, "precision": 0.7, "recall": 0.6, "f1": 0.65,
   "false_negatives": ["the printer is not working"], "false_positives": []},
 "spacy": {"library": "spaCy", "n": 40, "entity_precision": 0.9, "entity_recall": 0.8, "problem_accuracy": 0.6,
   "errors": [{"text": "printer broken", "expected": [], "got": []}]}}
```
`confusion_matrix.labels` follows CATEGORIES order. Rows = true labels. At most 5 examples per list. A section is `null` when its input is missing.

**examples.json** (library `"NLTK + spaCy"`): precomputed demo questions (2 per category, from the seed test split), so spaCy problem extraction can be shown:
```json
{"items": [{"id": "s017", "text": "My printer won't print!!", "category": "printer", "confidence": 0.93,
  "mood": {"compound": -0.31, "frustrated": true, "reasons": ["problem_phrase+exclaim"]},
  "entities": [{"text": "printer", "label": "DEVICE", "start_char": 3, "end_char": 10, "id": "printer"}],
  "problems": [{"thing": "printer", "problem": "not print", "negated": true}]}]}
```

**nltk_manifest.json** (library `"NLTK"`):
```json
{"base_url": "nltk_data/", "fs_root": "/nltk_data",
 "items": ["corpora/stopwords/english", "sentiment/vader_lexicon/vader_lexicon.txt"],
 "python_base_url": "py/", "python_files": ["nlp/__init__.py", "nlp/nltk_features.py", "nlp/classifier.py"],
 "bytes": 412345, "nltk_version": "3.9.4"}
```

## 4. Python module APIs
### 4.1 `nlp/nltk_features.py` (owner nltk-expert). Must import in Pyodide: nltk + stdlib only, no spaCy, no sklearn, no numpy
```python
NEGATIONS = frozenset({"no", "not", "nor", "never", "cannot"})      # plus any token ending in "n't" is kept
FRUSTRATION_THRESHOLD = -0.4
FRUSTRATION_PHRASES: tuple[str, ...] = ("not working", "doesn't work", "won't", "can't", "broken", "crashed",
    "again", "nothing works", "tried everything", "keeps", "stuck", "frozen")
TOKEN_PATTERN = r"[a-z0-9]+(?:'[a-z]+)?"
def use_data_dir(path: str) -> None             # nltk.data.path.insert(0, path)
def tokenize(text: str) -> list[str]            # text.replace("’", "'").lower(); RegexpTokenizer(TOKEN_PATTERN)
def clean(text: str) -> list[str]               # tokenize, then drop stopwords unless in NEGATIONS or endswith("n't"), then PorterStemmer().stem
def lemmas(text: str) -> list[str]              # same filter, WordNetLemmatizer instead of stemmer. BUILD ONLY (needs wordnet)
def frustration(text: str) -> dict              # {"neg","neu","pos","compound": float, "frustrated": bool, "reasons": list[str], "library": "NLTK"}
def satisfaction(text: str) -> dict             # {"compound": float, "label": "positive"|"neutral"|"negative"}  (cut-offs +/-0.05)
def top_words(token_lists: list[list[str]], n: int = 25) -> list[dict]                 # FreqDist -> [{"word","count"}]
def top_phrases(token_lists: list[list[str]], n: int = 20, min_freq: int = 3) -> list[dict]
    # BigramCollocationFinder.from_documents(token_lists); apply_freq_filter(min_freq); score_ngrams(likelihood_ratio)
    # -> [{"phrase": "a b", "count": int, "score": float}]
```
- `clean` uses PorterStemmer, which needs **no data files**. WordNet stays at build time and is never shipped to the browser.
- Load stopwords and VADER lazily on first call and cache them, so importing the module never needs data.
- VADER: `SentimentIntensityAnalyzer(lexicon_file="sentiment/vader_lexicon/vader_lexicon.txt")` if `nltk.data.find` finds that path, else fall back to the default `SentimentIntensityAnalyzer()` (reads `sentiment/vader_lexicon.zip`).
- `frustrated` = `compound <= -0.4` (reason `"vader_negative"`) OR (a FRUSTRATION_PHRASES match AND (`"!!"` in text, reason `"problem_phrase+exclaim"`, or a word of 4+ letters in ALL CAPS, reason `"problem_phrase+caps"`)).

### 4.2 `nlp/spacy_features.py` (owner spacy-expert). Build time only
```python
ENTITY_LABELS = ("DEVICE", "APP", "OS", "ERROR_CODE")
JS_REGEX: list[dict]    # hand-written JS-compatible regexes for ERROR_CODE, e.g. 0x[0-9a-f]{8}, "error 404"
def build_nlp(model: str = "en_core_web_sm", patterns_path: str = "nlp/patterns/it_entities.jsonl") -> "Language"
    # spacy.load(model); nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": "LOWER"}); load JSONL patterns
def entities(doc) -> list[dict]     # {"text","label","start_char","end_char","id"}; ENTITY_LABELS plus ORG, PRODUCT
def problems(doc) -> list[dict]     # {"thing": lemma, "problem": "not print", "negated": bool}; nsubj/nsubjpass/dobj/attr + neg;
                                    # xcomp ("keeps dropping" -> "keep drop"); ADJ with nsubj ("printer broken" -> "broken")
def tags(doc) -> list[str]          # sorted unique lower lemmas of noun-chunk roots + DEVICE/APP/OS ents; no stop words; len >= 3
def analyze(texts: list[str], nlp, batch_size: int = 64) -> list[dict]   # nlp.pipe -> [{"entities","problems","tags"}]
def export_patterns(path: str, patterns_path: str = ..., hints_path: str = "nlp/patterns/category_hints.json") -> dict
```
`export_patterns` writes entity_patterns.json through `common.write_json(..., "spaCy")` and returns the payload. Phrase-string patterns become lower-case phrases. Token-list patterns with LOWER/TEXT/LEMMA as a string or `{"IN": [...]}` become the cartesian product joined by spaces (at most 50 per pattern). LEMMA values also get a plural `+s`. `"OP": "?"` tokens give both variants. Group by `id`. REGEX token patterns are not converted (JS_REGEX covers them). Count anything else in `skipped_patterns`.

### 4.3 `nlp/classifier.py` (owner ml-engineer). Top-level imports only json, math, re, collections and numpy; sklearn imported inside functions, so Pyodide can import it
```python
SIMPLE_STOP: frozenset[str]                       # ~40 common English stopwords, local tests only
def simple_clean(text: str) -> list[str]          # re.findall(TOKEN_PATTERN, text.replace("’","'").lower()) minus SIMPLE_STOP
def get_tokenizer(name: str) -> Callable[[str], list[str]]   # "nltk_clean_v1" -> nltk_features.clean; "simple_v1" -> simple_clean
def train(texts, labels, test_texts=None, test_labels=None, tokenizer: str = "nltk_clean_v1") -> tuple[vec, clf, dict]
def export_json(vec, clf, path: str, tokenizer: str = "nltk_clean_v1", extra: dict | None = None) -> dict
def predict_numpy(model: dict, text: str) -> dict
    # -> {"category": str, "confidence": float, "probabilities": {cls: float}, "known_terms": int, "unsure": bool, "library": "Neural network"}
```
- Vectorizer: `TfidfVectorizer(tokenizer=get_tokenizer(name), lowercase=False, token_pattern=None, preprocessor=None, stop_words=None, ngram_range=(1, 2), max_features=2000, min_df=1, sublinear_tf=True, norm="l2", smooth_idf=True)`. It is fitted on the training texts only.
- Model: `MLPClassifier(hidden_layer_sizes=(64,), solver="lbfgs", alpha=1e-3, max_iter=500, random_state=42)`.
- If test_texts are None, use a stratified 80/20 `train_test_split(random_state=42)`. The shipped model is the one trained on the train part, so the metrics describe exactly what ships. The returned metrics dict has the shape of `metrics.json["classifier"]`.
- `predict_numpy`, exactly:
  1. `toks = get_tokenizer(model["tokenizer"])(text)`.
  2. Grams: for n in ngram_range[0]..ngram_range[1], take `" ".join(toks[i:i+n])` for every i. This matches sklearn's `_word_ngrams`.
  3. Count grams that are in `vocabulary` (build a dict term -> column once). `tf = 1 + ln(count)` if sublinear_tf, else count.
  4. `x[col] = tf * idf[col]`. If norm is l2 and `||x|| > 0`, divide x by `||x||`.
  5. `h = relu(x @ W0 + b0)` (also support tanh, logistic, identity). `z = h @ W1 + b1`. Softmax with max subtraction.
  6. `unsure = known_terms == 0 or confidence < model["min_confidence"]`.
- Local tests use `tokenizer="simple_v1"`. `pipeline/build.py` exits with an error if it would publish `simple_v1` while `NETLIFY == "true"`.

### 4.4 `pipeline/feedback.py` (owner feedback-loop-engineer). Stdlib urllib only; nltk optional
```python
def load_feedback(token: str | None = None, site_id: str | None = None, path: str | None = None, form_name: str = "rating") -> list[dict]
    # path (or env HELPMATE_FEEDBACK_FILE) -> read JSON fixture. Else token=env NETLIFY_API_TOKEN, site_id=env SITE_ID:
    # GET /api/v1/sites/{site_id}/forms -> id of form "rating"; GET /api/v1/forms/{id}/submissions?per_page=100&page=N until empty.
    # No token -> []. HTTP errors -> warning + []. Never print the token.
    # Normalized rows: {"id","created_at","stars": int 1-5,"comment","question","category","format"}; invalid rows dropped;
    # emails and phone numbers are masked in comment and question.
def summarize(feedback: list[dict], sentiment: Callable[[str], dict] | None = None) -> dict   # ratings_summary payload without generated_at
def format_rank(summary: dict) -> dict[str, list[str]]
def training_rows(feedback: list[dict]) -> list[tuple[str, str]]   # stars >= 4, valid category, len(question) >= 8
```
`sentiment` is `nltk_features.satisfaction` on Netlify. When it is None, `avg_compound` is 0.0 and the sentiment counts are null.

### 4.5 `pipeline/build.py` (owner build-pipeline-engineer)
`def main(argv: list[str] | None = None) -> int`. CLI: `python pipeline/build.py [--out site] [--allow-missing]`. Run from the repo root; insert the repo root into sys.path.
Steps:
1. Validate `data/content/*.json` against section 3 (fail loudly).
2. NLTK data: `nltk.download(pkg, download_dir=".cache/nltk_data", quiet=True)` for stopwords, vader_lexicon, wordnet and omw-1.4; then `use_data_dir(".cache/nltk_data")`. Copy only `corpora/stopwords/english` and `sentiment/vader_lexicon/vader_lexicon.txt` to `<out>/nltk_data/`, extracting from the `.zip` with `zipfile` when there is no unzipped copy (vader_lexicon is normally left zipped by the downloader). WordNet is used only at build time and is not published.
3. load_feedback, summarize and training_rows.
4. Train on seed (`split == train`) + tickets + feedback rows; test on seed rows with `split == test`; write model.json.
5. spaCy: build_nlp, then tags for answers and lessons -> topics.json, answers.json (+ `format_rank`), lessons.json; export_patterns; examples.json.
6. nltk_stats.json, then metrics.json (classifier + VADER on the seed `frustrated` column + spaCy on spacy_gold.jsonl). Also write `reports/classifier.md`.
7. Copy the Python files to `<out>/py/nlp/` and write nltk_manifest.json last.
- Without `--allow-missing`, a missing nltk, spacy or en_core_web_sm exits 1. With it (local tests only, e.g. `--out /tmp/x`), skip those steps, train with `simple_v1`, and print what was skipped. `--allow-missing` is refused when `NETLIFY == "true"`.

## 5. Environment, NLTK data and pins
`requirements.txt` (build, Python 3.12):
```
nltk==3.9.4               # same version as Pyodide's nltk, so clean() gives identical tokens in the build and the browser
spacy>=3.8.7,<3.9.0       # 3.8.x has Python 3.12 wheels; en_core_web_sm comes from the build command, not from here
scikit-learn==1.9.1       # same as the local test env; the model ships as JSON, so it does not need to match Pyodide
numpy>=2.0,<3
```
`requirements-dev.txt`: `-r requirements.txt`, `pytest`, `pytest-playwright`.
`netlify.toml` (netlify-engineer):
```toml
[build]
  command = "pip install -r requirements.txt && python -m spacy download en_core_web_sm && python pipeline/build.py"
  publish = "site"
[build.environment]
  PYTHON_VERSION = "3.12"
[[headers]]
  for = "/data/*"
  [headers.values]
    Cache-Control = "public, max-age=0, must-revalidate"
[[headers]]
  for = "/nltk_data/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"
```
Environment variables, set in the Netlify UI and never committed: `NETLIFY_API_TOKEN` (personal access token, build scope) and `BUILD_HOOK_URL` (Functions scope, used only by rebuild.mjs). `SITE_ID` and `NETLIFY` are set by Netlify itself.
Pyodide (browser): pin one CDN version (docs say 314.0.8 ships nltk 3.9.4). `pyodide.loadPackage(["nltk", "numpy"])`. Fetch the manifest `items` into `fs_root` and the `python_files` into `/home/pyodide/`, then `nlp.nltk_features.use_data_dir("/nltk_data")`. Run Pyodide in a Web Worker.

## 6. Phases, owners, done-when
| # | Owner | Inputs | Outputs | Done when |
|---|---|---|---|---|
| 1a | dataset-curator | docs/03, data-labeling, dataset-licensing | data/seed_questions.csv (>= 25 per category, 200+, `frustrated` 0/1, `split` train/test stratified 20%, seed 42), data/spacy_gold.jsonl (>= 40 lines `{"text","entities":[{"text","label"}],"problems":[{"thing","problem"}]}`), data/fetch_tickets.py, data/README.md | CSV parses; all 8 ids present; 4+ test rows per category; >= 20% frustrated; licenses recorded |
| 1b | instructional-designer | section 3 schemas, instructional-content, docs/05 | data/content/answers.json, data/content/lessons.json | 8 answers x 4 formats with equal step counts; 8 x 10 lessons; plain words (no jargon); valid JSON |
| 2a | ml-engineer | data/*.csv | nlp/__init__.py, nlp/common.py (do this first; others code against section 2), nlp/classifier.py, tests/test_classifier.py | pytest passes here with simple_v1; predict_numpy matches predict_proba (atol 1e-4 after rounding) and argmax on every test row |
| 2b | nltk-expert | section 4.1 | nlp/nltk_features.py, tests/test_nltk_features.py | `python -c "import ast; ast.parse(...)"` passes; no forbidden imports (test greps); tests importorskip nltk |
| 2c | spacy-expert | section 4.2, data/spacy_gold.jsonl | nlp/spacy_features.py, nlp/patterns/*.json(l), tests/test_spacy_features.py | JSONL lines are valid EntityRuler patterns; patterns cover every category; tests importorskip spacy |
| 3a | build-pipeline-engineer | phases 1-2 | pipeline/__init__.py, pipeline/build.py, tests/test_build.py, tests/fixtures/site_data/*.json (one valid sample of every section 3 file, `"fixture": true`) | `python pipeline/build.py --out /tmp/hm --allow-missing` succeeds here; fixtures validate |
| 3b | feedback-loop-engineer | section 4.4 | pipeline/feedback.py, data/feedback_sample.json, tests/test_feedback.py, README section "Ratings loop" | tests pass here; no token in logs; empty feedback works |
| 3c | netlify-engineer | section 5 | netlify.toml, requirements*.txt, .gitignore, netlify/functions/rebuild.mjs (`export const config = { schedule: "@daily" }`, POST to `process.env.BUILD_HOOK_URL`), README deploy steps | toml parses (tomllib); no secrets in repo |
| 4a | ux-accessibility-designer | brand, accessible-ui | site/css/tokens.css, docs/ui-spec.md (layout, badge styles, states: loading, unsure, frustrated, error) | contrast >= 4.5:1 for every text pair; 44 px targets |
| 4b | frontend-engineer | 4a, fixtures | site/index.html (+ static hidden `rating` form), css/helpmate.css, js/app.js, formats.js, speech.js, progress.js, rating.js, entities.js, assets/brand/ | works with fixtures and Pyodide stubbed; every result has a badge; progress uses key `helpmate.progress.v1` |
| 4c | pyodide-engineer | sections 3, 4.3, 5 | site/js/brain.js, site/js/brain-worker.js | `brain.js` exports `ready(): Promise<void>` and `analyze(text): Promise<{category, confidence, probabilities, unsure, mood:{compound, frustrated, reasons}, library}>`; if Pyodide fails, it rejects and app.js falls back to entity `category_hint` (badged spaCy) |
| 4d | data-viz-expert | nltk_stats, ratings_summary, metrics fixtures | site/insights.html, js/insights.js, js/charts.js, css/insights.css | charts have text and table alternatives; labels name the library |
| 5a | qa-engineer | everything | tests/test_site_json.py, tests/browser/test_app.py; run `pytest -q` | all tests pass or skip for a stated reason; browser tests serve a temp copy of site/ + fixtures; Pyodide tests skip without network |
| 5b | nlp-evaluator | metrics, data | reports/quality.md, reports/figures/*.svg | honest numbers, 3-5 real errors per component; states which numbers came from the local simple_v1 run and which need the Netlify build |

Each step is checked by Atlas: the files exist, `pytest -q` passes, the JSON loads, and nothing breaks the architecture rules. Failures go back to the owner with the exact error.
Progress localStorage: key `helpmate.progress.v1`, value `{"version": 1, "format_pref": "see_it", "categories": {"printer": {"done": [1, 2], "correct": [1], "badge": false, "updated": "<iso>"}}}`. Always wrap reads and writes in try/catch.
Rating form fields (static HTML in index.html, `name="rating"`, `data-netlify="true"`, `netlify-honeypot="bot-field"`): `form-name`, `bot-field`, `stars` (1-5), `comment` (max 500), `question` (max 300), `category` (id), `format` (FORMATS id), `model_generated_at`. AJAX POST to `/` as `application/x-www-form-urlencoded`. The note above the form says "Please don't include personal details".

## 7. UI labeling rule
Every result panel shows one badge, styled as a pill with text (never color alone):
| Panel | Badge |
|---|---|
| Category ("This sounds like a Printer question") | Neural network |
| Mood / calm tone switch | NLTK |
| Things you mentioned (entity matches from entity_patterns.json) | spaCy |
| Answer topics, lesson tags | spaCy |
| Example question breakdown (examples.json) | NLTK + spaCy |
| Insights: common words and phrases | NLTK |
| Insights: rating trends | NLTK (comment sentiment) |
| Insights: model quality | Neural network, NLTK, spaCy (one per section) |
| Fallback category when Pyodide is unavailable | spaCy (vocabulary match) |
Tooltip text: "Made by NLTK in your browser", "Made by spaCy when the site was built", "Made by HelpMate's neural network in your browser".

## 8. Risks
1. NLTK and spaCy code cannot be run here, so the first real run is on Netlify. Mitigation: importorskip tests, `--allow-missing` local build, and reading the deploy log closely on the first deploy.
2. No network: the public ticket sample cannot be fetched here. The classifier trains on the seed set (200+) alone unless someone runs `data/fetch_tickets.py` elsewhere.
3. Token parity between the build and the browser depends on nltk being the same version (3.9.4). Verify Pyodide's nltk version and the CDN URL before the deploy; if they differ, change the pin.
4. model.json is about 1-1.5 MB. Mitigation: 6 significant digits and Netlify compression. Cut max_features to 1500 if it goes over 2 MB.
5. VADER misses technical negatives; the phrase rule helps. Report the errors, don't hide them.
