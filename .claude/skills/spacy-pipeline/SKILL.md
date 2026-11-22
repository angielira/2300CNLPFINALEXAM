---
name: spacy-pipeline
description: "Load and run spaCy's en_core_web_sm efficiently at build time. Use for any spaCy processing in pipeline/."
---

# spacy-pipeline

Used by: spacy-expert, build-pipeline-engineer

## Recipe
```python
import spacy
nlp = spacy.load("en_core_web_sm")
for doc in nlp.pipe(texts, batch_size=64):
    ...
```
- Install in the Netlify build: `python -m spacy download en_core_web_sm`.
- Use `nlp.pipe` for many texts; disable unused components with `nlp.select_pipes(disable=[...])` when only some are needed.
- spaCy is not available in Pyodide: save results as JSON for the browser.
