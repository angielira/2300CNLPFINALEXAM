---
name: static-json-output
description: "Write the static JSON files the HelpMate site reads, with the shared envelope and the right library label. Use whenever a build step produces data for the browser."
---

# static-json-output

Used by: spacy-expert, ml-engineer, build-pipeline-engineer, feedback-loop-engineer

Binding contract: `reports/plan.md` sections 2 and 3. If anything here differs from the plan, the plan wins.

## Always write through `nlp.common.write_json`
```python
write_json(path, payload: dict, library: str, compact: bool = False) -> pathlib.Path
```
- Adds `generated_at` (`utc_now()`, e.g. `"2026-11-22T10:00:00Z"`), `library` and `schema_version` (1).
- `library` must be one of `LIBRARIES = ("NLTK", "spaCy", "Neural network", "NLTK + spaCy")`.
- Creates parent folders. UTF-8, `ensure_ascii=False`, `sort_keys=True`; `compact=True` uses `separators=(",", ":")`, otherwise `indent=1`.

## Envelope
Every file: `{"generated_at": str, "library": <one of LIBRARIES>, "schema_version": 1, "items": [...], ...}`.

## Files in `site/data/` and their library
| File | library |
|---|---|
| answers.json | `"NLTK + spaCy"` (text by the team, `tags` from spaCy, `format_rank` from NLTK-scored ratings) |
| lessons.json | `"spaCy"` |
| entity_patterns.json | `"spaCy"` |
| topics.json | `"spaCy"` |
| nltk_stats.json | `"NLTK"` |
| model.json | `"Neural network"`, written with `compact=True` |
| ratings_summary.json | `"NLTK"` (aggregates only, no comment or question text) |
| metrics.json | top level `"Neural network"`; each section has its own `library` (see below) |
| examples.json | `"NLTK + spaCy"` |
| nltk_manifest.json | `"NLTK"` |

## metrics.json sections
- `classifier.library = "Neural network"`, `vader.library = "NLTK"`, `spacy.library = "spaCy"`; top-level `items` is `[]`.
- A section is `null` when its input is missing. At most 5 examples per list. `confusion_matrix.labels` follows CATEGORIES order; rows are true labels.

## Rules
- Raw size < 1 MB per file, except model.json < 2 MB.
- Category order is always the CATEGORIES order from `nlp/common.py`.
- The browser treats any missing file as "not ready yet" and never crashes.
- Validate with `json.load` in tests; fixtures in `tests/fixtures/site_data/` carry `"fixture": true`.
