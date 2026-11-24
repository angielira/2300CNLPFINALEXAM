# Architecture decision records

One decision per file, numbered in order, never reused. To change a decision, add a new ADR that supersedes the old one.
Format: Nygard (status, context, decision, consequences) plus alternatives considered. Overview: [../architecture.md](../architecture.md).

| # | Decision | Status | Date |
|---|---|---|---|
| [0001](0001-static-site-on-netlify-no-server.md) | Ship HelpMate as a static site on Netlify, with no server | accepted | 2026-11-23 |
| [0002](0002-nlp-at-build-time-spacy-not-in-browser.md) | Run NLP at build time and never run spaCy in the browser | accepted | 2026-11-23 |
| [0003](0003-pyodide-module-worker-for-live-nltk-and-classifier.md) | Run NLTK and the classifier live in a Pyodide module Web Worker | accepted | 2026-11-23 |
| [0004](0004-mlp-exported-as-json-numpy-inference.md) | Export the MLP classifier as JSON and run it with NumPy | accepted | 2026-11-23 |
| [0005](0005-netlify-forms-and-localstorage-instead-of-database.md) | Use Netlify Forms and localStorage instead of a database | accepted | 2026-11-23 |
| [0006](0006-ratings-loop-via-rebuilds.md) | Close the ratings loop through rebuilds, not in real time | accepted | 2026-11-23 |

Every new dependency, runtime location or third-party script needs a new ADR (boundary checklist: `.claude/skills/architecture-decisions/SKILL.md`).
