---
name: dependency-parsing
description: "Extract what is broken from a question as (thing, problem) pairs using spaCy's dependency parse. Use for problem extraction and its evaluation."
---

# dependency-parsing

Used by: spacy-expert, nlp-evaluator

## Recipe
```python
def problems(doc):
    out = []
    for tok in doc:
        if tok.pos_ == "VERB" or tok.dep_ == "ROOT":
            subj = [c for c in tok.children if c.dep_ in ("nsubj", "nsubjpass")]
            obj = [c for c in tok.children if c.dep_ in ("dobj", "attr")]
            neg = any(c.dep_ == "neg" for c in tok.children)
            thing = (subj or obj or [None])[0]
            if thing is not None:
                out.append({"thing": thing.lemma_, "problem": ("not " if neg else "") + tok.lemma_})
    return out
```
- Example: "My printer won't print" -> `{"thing": "printer", "problem": "not print"}`.
- Use `displacy.render(doc, style="dep")` to inspect failures; save SVGs to `reports/` for the write-up.
