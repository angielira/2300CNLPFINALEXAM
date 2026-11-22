# 2. What spaCy does best for HelpMate

**Role in the app:** spaCy does the *deep linguistic analysis* at build time: it recognizes the devices, apps and error codes people mention, works out what is broken, and tags every answer and lesson so the live app can find them. spaCy does not run in Pyodide, so its results are saved as static JSON. ([Pyodide packages](https://pyodide.org/en/stable/usage/packages-in-pyodide.html))

| HelpMate feature | spaCy tool | Output |
|---|---|---|
| Recognize devices, apps, OS, error codes | `EntityRuler` added before `ner` in `en_core_web_sm` | Labels like `DEVICE`, `APP`, `OS`, `ERROR_CODE` |
| Find what is broken ("printer → won't print") | Dependency parse: `token.dep_`, `token.head`, negation (`neg`) | (thing, problem) pairs |
| Tag help articles and lessons by topic | `doc.noun_chunks`, `token.lemma_` | Topic tags in `lessons.json` |
| Spot brands and companies | Built-in `ORG` / `PRODUCT` entities | Extra tags |
| Show the analysis visually | `displacy` (entity and dependency views) | Images for the report |

## EntityRuler for IT vocabulary

- The EntityRuler adds entities to `Doc.ents` with token-based rules or exact phrase matches. A pattern is a dict with `"label"` and `"pattern"`; the pattern is a phrase string or a list of token dicts, e.g. `{"label": "ORG", "pattern": "Apple"}`. ([spaCy EntityRuler API](https://spacy.io/api/entityruler))
- Add it with `nlp.add_pipe("entity_ruler", before="ner")` so custom labels win over the statistical model.
- Example patterns for HelpMate:
  - `{"label": "APP", "pattern": "Outlook"}`, `{"label": "OS", "pattern": [{"LOWER": "windows"}, {"LIKE_NUM": true}]}`
  - `{"label": "DEVICE", "pattern": [{"LEMMA": {"IN": ["printer", "router", "laptop", "webcam"]}}]}`
  - `{"label": "ERROR_CODE", "pattern": [{"TEXT": {"REGEX": "^0x[0-9A-Fa-f]{8}$"}}]}`
- **Export the patterns** (`ruler.to_disk(...)` writes JSONL, or dump the list to JSON) so the browser can reuse the same vocabulary for live matching with NLTK tokens.

## Extracting the problem with the dependency parse

Rule of thumb that works for short help questions:
1. Find the entity or noun that is the subject (`nsubj`) or object (`dobj`) of the main verb.
2. Keep the verb and any negation (`neg` child: "won't", "not", "can't").
3. Output `printer → won't print`, `password → forgot`, `wifi → keeps dropping`.

Report the failures honestly (long rambling questions, missing verbs like "printer broken").

## The model

`en_core_web_sm` is the small English pipeline (tok2vec, tagger, parser, attribute ruler, lemmatizer, NER). It is a trained **neural** pipeline (a CNN-based tok2vec feeds the parser and NER), which is worth saying in the report. ([spaCy models](https://spacy.io/models/en))

## Sources
- EntityRuler API: https://spacy.io/api/entityruler
- Rule-based matching (patterns, token attributes): https://spacy.io/usage/rule-based-matching
- Linguistic features (dependency parse, noun chunks, lemmas): https://spacy.io/usage/linguistic-features
- English models: https://spacy.io/models/en
- displaCy: https://spacy.io/usage/visualizers
