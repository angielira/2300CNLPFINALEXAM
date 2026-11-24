# HelpMate version 1 report

Author: Atlas (orchestrator). Date: 2026-11-23. Live site: https://helpmate2300nlp.netlify.app. Repository: https://github.com/angielira/2300CNLPFINALEXAM.
Sources: [requirements.md](requirements.md) (Nora), [architecture.md](architecture.md) and [adr/](adr/README.md) (Theo), [reports/security.md](../reports/security.md) (Kai), [reports/qa.md](../reports/qa.md) (Quinn), [reports/nlp_quality.md](../reports/nlp_quality.md) (Vera), [reports/plan.md](../reports/plan.md) (Atlas).

## 1. What was built

HelpMate is a static site on Netlify. Python (NLTK, spaCy, scikit-learn) runs only when Netlify builds the site and writes static JSON. The browser runs Pyodide (NLTK + NumPy) in a module Web Worker and plain JavaScript. There is no server and no database.

| Feature | Library shown to the user | Where it runs |
|---|---|---|
| Question box, 300-character limit, example chips, friendly empty and unsure states | (interface) | Browser, JavaScript |
| Topic sorting into 8 categories ("This sounds like an Email question") | **Neural network** (TF-IDF + MLP, 64 hidden units) | Trained at build; re-run with NumPy in Pyodide |
| Frustration detection and calm tone | **NLTK** (VADER + problem-phrase rule) | Browser, Pyodide |
| Question cleaning for the classifier (tokenize, negation-aware stop words, Porter stemming) | **NLTK** | Build and browser (same nltk 3.9.4) |
| "Things you mentioned" (DEVICE, APP, OS, ERROR_CODE) | **spaCy** (EntityRuler, exported as patterns) | Build; browser only matches the exported JSON |
| "What is broken" (thing, problem) for example questions | **spaCy** (dependency parse) | Build only |
| Answer and lesson topic tags | **spaCy** (noun chunks, lemmas) | Build only |
| Four formats: See it (numbered steps), Hear it (speech), Try it (checklist), Read it (printable) | (content by Maya) | Browser |
| 10-step mini-course per topic, progress and badges | **spaCy** tags; progress in localStorage | Browser |
| Fallback when Pyodide cannot start | **spaCy** (vocabulary match) | Browser |
| Star rating form | Netlify Forms; comment mood by **NLTK** at build | Browser + build |
| Insights page: common words and phrases, rating trends, model quality | **NLTK**, **spaCy**, **Neural network** (one label per section) | Build data, browser charts |
| Resources page with every source | (interface) | Browser |

Requirements status (32 stories): **21 Met, 10 Partly met, 1 Not met**. Of the 14 Must stories, 11 are Met and 3 Partly met (US-05 frustration recall, US-24 live screen-reader pass, US-25 reading level).

### Live in-browser check (2026-11-23, real Chrome, by the lead)
The first classic-worker `importScripts` load failed with "NetworkError ... failed to load". After switching to a module worker importing `pyodide.mjs` (ADR 0003), the live site loaded Pyodide 314.0.8 with nltk 3.9.4 and numpy 2.4.6; `brain.ready()` took about 12 s. A frustrated printer question was classified printer at 0.999 and flagged frustrated; the UI question "My Outlook email WONT send and I've tried everything!!" showed the NLTK calm notice and the Neural network card "Email 100% sure". Netlify Forms detection is enabled; no real rating has been submitted yet.

## 2. How the 19-agent team worked

The team lives in `.claude/agents/` (19 agents), with shared skills in `.claude/skills/` and sourced notes in `knowledge/<agent>/`. Atlas planned the work and file contracts in `reports/plan.md`, then ran it in phases:

1. **Data and content:** Tally (seed questions, spaCy gold file, licenses) and Maya (answers in four formats, 10-step lessons), in parallel.
2. **NLP:** Lex (NLTK), Sage (spaCy) and Synapse (classifier) in parallel, each coding against the shared `nlp/common.py` contract.
3. **Build and loop:** Brick (`pipeline/build.py`), Echo (ratings via Netlify Forms) and Nimbus (`netlify.toml`, rebuild function).
4. **Interface:** Iris (design and accessibility), then Pixel (app), Vega (Insights) and Pip (Pyodide worker) in parallel.
5. **Peer review:** Quinn (tests and QA report), Vera (honest NLP quality report) and Kai (security review) checked the others' work; failures went back to the owner with the exact error.
6. **Product and architecture:** Nora wrote requirements and checked every story against evidence; Theo wrote the architecture page and six ADRs. Forge (meta-agent) added agents, skills and knowledge notes when gaps appeared.

Atlas checked each handoff: the file exists, JSON loads, `pytest` passes, and the build-time/browser boundary holds (spaCy never in the browser).

## 3. Quality numbers (live Netlify build, `/data/metrics.json`, tokenizer `nltk_clean_v1`)

| Component | Measure | Value |
|---|---|---|
| Neural network | Accuracy / macro F1, 48 test questions | 0.75 / 0.757 (about ±12 points at this size) |
| Neural network | Weakest recall | passwords 0.44, video_calls 0.57, wifi 0.60 |
| NLTK VADER frustration | Precision / recall, all 240 seed rows | 0.63 / 0.42 |
| NLTK VADER frustration | Recall, 48 test rows (14 frustrated) | 0.29 (precision 0.67), below the 0.60 target |
| spaCy entities | Precision / recall | 0.98 / 0.99 |
| spaCy problem extraction | Exact / right thing | 0.36 / 0.45, below the 0.50 / 0.60 targets |

The data is small, synthetic and labeled by one person, so real-world numbers will likely be lower.

## 4. Tests and security

- **Tests:** `python3 -m pytest -q` gives **163 passed, 24 skipped, 0 failed**. The 24 skips need NLTK or spaCy installed locally; those paths run in the Netlify build. Browser tests stub Pyodide; the real path was checked by hand (section 1).
- **Security (Kai):** no API keys, tokens, build-hook URLs or private data in the working tree, the full git history, the built site or the live JS/JSON. Nothing to rotate. Hardening done: `X-Frame-Options`, `Permissions-Policy`, wider `.gitignore`, clearer rating privacy notice. A CSP is proposed but not yet applied.

## 5. Live links

- App: https://helpmate2300nlp.netlify.app
- Insights: https://helpmate2300nlp.netlify.app/insights.html
- Resources: https://helpmate2300nlp.netlify.app/resources.html
- Live metrics: https://helpmate2300nlp.netlify.app/data/metrics.json

## 6. What is left for version 2 (in priority order)

| # | Task | Owner | Why | Done when |
|---|---|---|---|---|
| 1 | Prove the ratings loop end to end | netlify-engineer (Nimbus) + feedback-loop-engineer (Echo) | Forms detection is on, but 0 real ratings, and `NETLIFY_API_TOKEN` / `BUILD_HOOK_URL` are not confirmed (US-17, 18, 21, 14) | A test rating shows under Forms > rating; after a rebuild `ratings_summary.json` total > 0 and Insights rating charts change |
| 2 | Raise frustration recall | nltk-expert (Lex), re-measured by nlp-evaluator (Vera) | Test recall 0.29 misses most frustrated users (US-05, a Must) | Test-split recall and precision both at least 0.60, threshold tuned on train rows only |
| 3 | Guard the loop against self-training and poisoning; keep rated words out of `model.json` | feedback-loop-engineer (Echo) + ml-engineer (Synapse) | ADR 0006 risk; Kai F8/F9/R3 | Feedback rows capped per category; feedback-only terms need `min_df=2` or seed vocabulary; names/addresses masked; test proves a one-off surname never reaches `model.json` |
| 4 | Apply the Content-Security-Policy and check live headers | netlify-engineer (Nimbus) + pyodide-engineer (Pip) | Kai F13/R1; ADR 0001 | `curl -sI` shows the new headers; CSP runs report-only on a preview, then enforced, with the live box still working |
| 5 | Improve problem extraction and fix the gold file | spacy-expert (Sage); scope decision with software-architect (Theo) | Exact 0.36, thing 0.45; shown only for precomputed examples (US-04, ADR 0002) | Exact at least 0.50, thing at least 0.60 on a corrected gold file; decision recorded on a JS rule for typed questions |
| 6 | Live accessibility pass and reading-level check | ux-accessibility-designer (Iris) + qa-engineer (Quinn); instructional-designer (Maya) | US-24 criterion 6 and US-25 criterion 3 are the remaining Must gaps | Keyboard-only and screen-reader pass on the live site with no blockers; readability measured at US grade 6-7 or lower |
| 7 | Automated tests against the live URL and the missing browser tests | qa-engineer (Quinn) | The real Pyodide path was checked by hand only; no tests for Try-it ticks after reload, badge at 10 steps, unsure chip click | Browser suite runs against the live URL in CI and covers those three cases |
| 8 | Insights fixes | data-viz-expert (Vega) + build-pipeline-engineer (Brick) | Problem-accuracy ceiling never written; confusion-matrix headers break and columns are cut off (US-22) | `problem_ceiling` in `metrics.json` and shown; table readable at 1280 px |
| 9 | Stronger classifier on weak classes | ml-engineer (Synapse) + dataset-curator (Tally) | passwords recall 0.44, video_calls 0.57; one author, synthetic data | Re-check settings with `nltk_clean_v1`; clearer labeling rules; more test questions; recall at least 0.60 for every class |
| 10 | Self-host Pyodide and fonts; add secret scanning | pyodide-engineer (Pip); security-reviewer (Kai) | Kai R2, R6: removes jsDelivr and Google Fonts trust; protects the public repo | Pyodide and fonts served from `'self'`; gitleaks or detect-secrets in CI; GitHub push protection on |
| 11 | Pictures for See it steps | instructional-designer (Maya) + ux-accessibility-designer (Iris) | US-32 (Could) | Every step has an image under 50 KB with alt text, readable at 360 px |
| 12 | Brand font cleanup | ux-accessibility-designer (Iris) | Pages load Fredoka, which the brand does not list (US-31) | Only Nunito loaded, or Fredoka added to the brand on purpose |
| 13 | Knowledge gaps | meta-agent (Forge) | Kai R7: no sourced notes on `Permissions-Policy` or scheduled-function URL access | Both notes in `knowledge/security-reviewer/` with official sources |
