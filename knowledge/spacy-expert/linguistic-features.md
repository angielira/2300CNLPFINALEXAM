# spaCy linguistic features

- POS: `token.pos_` (UPOS) and `token.tag_` (fine-grained); `spacy.explain(tag)`.
- Dependencies: `token.dep_`, `token.head`, `token.children`, `token.subtree`, `lefts`/`rights`, `ancestors`. Check `doc.has_annotation("DEP")`.
- Noun chunks: `doc.noun_chunks` -> spans with `.root`, `.root.dep_`, `.root.head`.
- Lemmas: `token.lemma_` (needs the `lemmatizer` component; trained pipelines include it).
- Entities: `doc.ents`, `ent.label_`, `ent.start_char`, `ent.end_char`; `token.ent_type_`, `token.ent_iob_`.
- Retokenize with `with doc.retokenize() as r: r.merge(span)`.

## Sources
- https://spacy.io/usage/linguistic-features
