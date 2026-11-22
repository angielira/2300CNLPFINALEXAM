# HelpMate QA report (Quinn, phase 5a)

## Result
`python3 pipeline/build.py --allow-missing` succeeds (tokenizer simple_v1, accuracy 0.667, 192 train, 40 ratings).
`python3 -m pytest -q`: **129 passed, 18 skipped, 0 failed** (about 23 s).
The 18 skips are all "nltk / spaCy not installed here" (1 in test_brain_python_path, 1 in test_nltk_features, 16 in test_spacy_features). They run on Netlify.

## What was tested
| File | Covers |
|---|---|
| tests/test_site_json.py (14) | Every site/data/*.json has the envelope (schema_version 1, library in LIBRARIES, generated_at ending Z, items list) and its key fields; answers and lessons cover all 8 categories; 10 steps per lesson; model.json shapes consistent; no secret-looking strings. |
| tests/browser/test_app.py (12) | Index loads with no page errors; "my printer wont print!!" gives category card with badge, at least 2 badges; fallback notice when the engine is missing; 4 format buttons switch (aria-pressed, 4 different panels) and Hear it has play/pause/stop; side panel opens, quiz answer saves `helpmate.progress.v1`, Escape closes, progress bar shows 1 after reload; static Netlify rating form in the HTML source (data-netlify, honeypot, all 8 fields, 5 star radios, maxlength 500); honeypot hidden and tabindex -1; stars radio fix (row is position:relative, clicking the label checks the radio, radio sits inside the row, keyboard works); stubbed brain.js returning a frustrated printer result shows Neural network badge on the category card, NLTK badge on the mood card and the calm notice, no fallback notice; empty question error; 360 px no horizontal overflow (page and open panel); a11y: one h1, lang, every button named, images have alt, form controls labelled, main buttons >= 44 px. |
| tests/browser/test_insights.py (8) | No page errors; null sections show "This appears after the Netlify build."; every chart section has a library badge; a11y basics and 44 px targets; 360 px no overflow; screenshots at 1280 and 375; with routed sample NLTK stats the word chart draws and the notice goes away. |

Browser tests serve a temp copy of site/ on a free port (conftest.py) and block fonts and CDN requests. Screenshots: reports/screens/insights-1280.png and insights-375.png (plus the earlier home, panel and stub-brain shots).

## Bugs
- No functional bugs found. I changed no front-end files.
- The stars fix (`.stars__row { position: relative }`, app.css line 490) works.
- Minor, cosmetic (insights.html at 1280, from the screenshot, not fixed): in the confusion-matrix table the narrow header cells break words mid-word ("Print er", "Pass word s & Login"), and the table's right columns are cut off and need horizontal scroll inside the card. Suggest Vega give the header cells `overflow-wrap: normal; hyphens: none` and a min-width, or shorten the labels.
- Minor: the footer badges wrap onto two lines at 1280 ("Neural network" on its own line). Cosmetic only.
- Note: an old `python3 -m http.server 8765` (pid 741) was already running when I started. It is not mine, so I left it.

## Only verifiable after deploy
- The real Pyodide path (CDN load, NLTK wheel and data download, worker, VADER, NumPy classifier in browser). Here Pyodide is blocked, so only the fallback path and a stubbed brain were tested.
- The real NLTK and spaCy build: nltk_stats items, top_phrases, VADER and spaCy metrics, nltk tokenizer (not simple_v1), entity_patterns from spaCy, token parity between build and browser (nltk version 3.9.4 vs Pyodide's).
- Netlify Forms detection and real submissions; the build hook; real ratings flowing into ratings_summary.json.
- Real browser speech (Hear it) audio, screen reader behaviour, real contrast in the deployed CSS with fonts loaded.

## Post-deploy checklist
1. Netlify deploy log: build passes; no "SKIPPED" line in the build summary (NLTK, tokenizer, spaCy all ran); `--allow-missing` not used.
2. Open `/data/model.json`, `/data/nltk_stats.json`, `/data/metrics.json`: library names correct, tokenizer is nltk (not simple_v1), n_documents > 0.
3. Home: ask "my printer wont print!!". Expect "Neural network" and "NLTK" badges and no "smart helper couldn't start" notice. Ask a frustrated one ("my stupid printer STILL wont print") and check the calm notice.
4. Check the browser console for errors; check the nltk version Pyodide loaded.
5. Click all four formats; Hear it plays and stops; Try it ticks persist after reload.
6. Open the side panel, answer a quiz question, reload, progress remains; finish 10 steps and check the badge.
7. Submit a rating; confirm it appears in Netlify Forms > rating (fields stars, comment, question, category, format, model_generated_at), and the honeypot field is empty.
8. Trigger the build hook; confirm Insights ratings update, and no "appears after the Netlify build" notices remain.
9. Insights at 1280 and 375 px: no horizontal page scroll; charts and "Show this as a table" work.
10. Re-run the browser tests against the live URL (change the base_url fixture) and a keyboard-only pass.
