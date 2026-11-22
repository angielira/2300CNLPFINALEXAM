---
name: testing
description: "Write and run HelpMate's pytest and Playwright tests. Use before any sign-off or after a fix."
---

# testing

Used by: build-pipeline-engineer, qa-engineer, nlp-evaluator

## Python
- Files `tests/test_*.py`, functions `test_*`; plain `assert`.
- Cover: text cleaning, VADER thresholds, EntityRuler matches, problem extraction, NumPy-vs-sklearn parity, every `site/data/*.json` loads.
- Run: `pytest -q`.

## Browser (optional if tooling is available)
- `pip install pytest-playwright && playwright install`.
- Test: question box returns a labeled result; format buttons switch; side panel progress survives reload.
