---
name: entity-ruler-patterns
description: "Write, save and export spaCy EntityRuler patterns for devices, apps, operating systems and error codes. Use when adding IT vocabulary."
---

# entity-ruler-patterns

Used by: spacy-expert, dataset-curator, pyodide-engineer

## Recipe
```python
ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.add_patterns([
    {"label": "APP", "pattern": "Outlook", "id": "outlook"},
    {"label": "APP", "pattern": [{"LOWER": "outlook"}], "id": "outlook"},
    {"label": "OS", "pattern": [{"LOWER": "windows"}, {"LIKE_NUM": True, "OP": "?"}]},
    {"label": "DEVICE", "pattern": [{"LEMMA": {"IN": ["printer", "router", "laptop", "webcam", "phone"]}}]},
    {"label": "ERROR_CODE", "pattern": [{"TEXT": {"REGEX": "^0x[0-9A-Fa-f]{8}$"}}]},
])
ruler.to_disk("nlp/patterns/it_entities.jsonl")
```
- Before `ner`: the statistical model respects the ruler's spans.
- `id` groups spelling variants into one entity (`ent.ent_id_`).
- Export a simple JSON list `{label, phrases}` to `site/data/entity_patterns.json` so the browser can match the same terms.
