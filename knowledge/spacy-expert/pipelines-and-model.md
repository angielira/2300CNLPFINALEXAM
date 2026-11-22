# Pipelines and en_core_web_sm

- `spacy.load("en_core_web_sm")` loads the small English pipeline (tok2vec, tagger, parser, attribute ruler, lemmatizer, ner).
- Install: `python -m spacy download en_core_web_sm`.
- Process many texts with `nlp.pipe(texts, batch_size=...)`.
- The pipeline's components are trained neural models.
- spaCy is not in Pyodide's package list, so it runs only at build time.

## Sources
- https://spacy.io/models/en
- https://spacy.io/usage/processing-pipelines
- https://pyodide.org/en/stable/usage/packages-in-pyodide.html
