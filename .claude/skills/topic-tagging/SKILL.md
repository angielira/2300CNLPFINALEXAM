---
name: topic-tagging
description: "Tag answers and lessons with topics using spaCy noun chunks and lemmas. Use when building topics.json or linking questions to lessons."
---

# topic-tagging

Used by: spacy-expert, instructional-designer

## Recipe
```python
def tags(doc):
    chunks = {c.root.lemma_.lower() for c in doc.noun_chunks}
    ents = {e.text.lower() for e in doc.ents if e.label_ in {"DEVICE", "APP", "OS"}}
    return sorted(chunks | ents)
```
- Lemmas merge "printers"/"printer".
- Store as `site/data/topics.json`: `{answer_id: [tags]}` with `"library": "spaCy"`.
