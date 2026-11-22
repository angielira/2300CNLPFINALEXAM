# Running spaCy at build time

- Install the model in the build command: `python -m spacy download en_core_web_sm`.
- Use `nlp.pipe(texts, batch_size=64)` for speed.
- Save results as JSON (spaCy can't run in the browser).

## Sources
- https://spacy.io/usage/processing-pipelines
- https://spacy.io/api/language#pipe
