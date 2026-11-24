# 0002. Run NLP at build time and never run spaCy in the browser
Date: 2026-11-23
Status: accepted

## Context
- spaCy is not in Pyodide's package list, so it cannot run in the browser (docs/06-netlify-architecture.md).
- `en_core_web_sm` plus spaCy would be a very large download for a non-technical user even if it could run.
- Most spaCy work in HelpMate is about fixed content: tagging answers and lessons, exporting the IT vocabulary, analysing demo questions and measuring quality.
- Static hosting (ADR 0001) means the build is the only place where Python can run on Netlify.

## Decision
We will run NLTK, spaCy and training in `pipeline/build.py` and write the results as static JSON in `site/data/`
through `nlp.common.write_json`, which adds `generated_at`, `library` and `schema_version`. The build writes
`answers.json`, `lessons.json`, `topics.json`, `entity_patterns.json`, `examples.json`, `nltk_stats.json`,
`metrics.json`, `ratings_summary.json`, `model.json` and `nltk_manifest.json` (contracts in `reports/plan.md` section 3).
For live questions, spaCy's EntityRuler patterns are exported as lower-case phrases plus JS regexes
(`entity_patterns.json`) and matched in JavaScript (`site/js/entities.js`). `nlp/spacy_features.py` is not copied to the site
(`PY_FILES` in `build.py` lists only `nlp/__init__.py`, `nlp/nltk_features.py`, `nlp/classifier.py`).

## Consequences
- Positive: spaCy's full pipeline (dependency parse, noun chunks, EntityRuler) is used where it can run, and its results are free to read in the browser.
- Positive: the browser treats a missing file as "not ready yet" (`getJSON` in `site/js/dom.js` returns null).
- Positive: `export_patterns` needs no spaCy install, so the browser always gets the IT vocabulary, even in a local `--allow-missing` build.
- Negative: live questions get only phrase/regex entity matching, not spaCy's parse. "What is broken" (problem extraction) is shown only for the precomputed `examples.json`, not for the user's own question. The UI must label this honestly (badge "spaCy", "made when the site was built").
- Negative: a build must succeed for any content change; the build fails loudly (exit 1) if spaCy or `en_core_web_sm` is missing on Netlify.
- Negative: each build downloads NLTK data (`nltk.download`) and `en_core_web_sm`, so a network problem at build time fails the deploy. The previous deploy stays live.

## Alternatives considered
- **spaCy in the browser:** not possible in Pyodide.
- **A JavaScript NLP library (compromise, wink-nlp) for live parsing:** a second NLP stack with different results from the build, and not part of the course brief. Rejected.
- **A hosted spaCy API:** needs a server (rejected in ADR 0001).
