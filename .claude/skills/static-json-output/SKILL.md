---
name: static-json-output
description: "Write the static JSON files the HelpMate site reads, with a consistent shape. Use whenever a build step produces data for the browser."
---

# static-json-output

Used by: spacy-expert, ml-engineer, build-pipeline-engineer, feedback-loop-engineer

## Rules
- All files go in `site/data/`.
- Each file has `{"generated_at": ISO-8601, "library": "NLTK" | "spaCy" | "Neural network" | "NLTK + spaCy", "items": [...]}`.
- UTF-8, `ensure_ascii=False`, sorted keys for stable diffs.
- Keep files small (< 1 MB each); the browser downloads them.
- Validate with `json.load` in tests.
