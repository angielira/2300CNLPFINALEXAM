# Build order and handoffs

1. dataset-curator -> `data/`
2. nltk-expert, spacy-expert, ml-engineer -> `nlp/`
3. instructional-designer -> `site/data/answers.json`, `site/data/lessons.json`
4. build-pipeline-engineer -> `pipeline/build.py` (runs everything)
5. ux-accessibility-designer + frontend-engineer + data-viz-expert -> `site/`
6. pyodide-engineer -> live box
7. feedback-loop-engineer + netlify-engineer -> Forms, `netlify.toml`, build hook docs
8. qa-engineer + nlp-evaluator -> `tests/`, `reports/`

Done when: `python pipeline/build.py` succeeds locally, `pytest -q` passes, every panel is labeled NLTK / spaCy / Neural network, README has deploy steps.

## Sources
- docs/expert-roster.md (this repo)
