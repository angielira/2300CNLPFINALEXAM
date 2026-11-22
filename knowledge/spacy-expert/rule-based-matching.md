# Rule-based matching and the EntityRuler

- Matcher token patterns: one dict per token; keys `ORTH`/`TEXT`, `LOWER`, `LEMMA`, `POS`, `LIKE_NUM`, `IS_DIGIT`, `REGEX`; `IN`/`NOT_IN` for lists; `OP` = `?`, `+`, `*`, `!`.
- PhraseMatcher for long term lists; `attr="LOWER"` for case-insensitive.
- EntityRuler: `nlp.add_pipe("entity_ruler", before="ner")` so the model respects its spans (after `ner` it only fills gaps unless `overwrite_ents=True`).
- Pattern = `{"label", "pattern", optional "id"}`; `id` is stored in `ent.ent_id_` to merge variants.
- Save/load patterns as JSONL with `ruler.to_disk(path)` / `ruler.from_disk(path)`.

## Sources
- https://spacy.io/usage/rule-based-matching
- https://spacy.io/api/entityruler
