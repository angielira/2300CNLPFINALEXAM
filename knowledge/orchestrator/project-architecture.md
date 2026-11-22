# HelpMate architecture (summary for planning)

- **Build time (Netlify, Python):** NLTK statistics and VADER, spaCy entities/problems/tags, MLP training, feedback ingestion -> static JSON in `site/data/`.
- **Browser:** Pyodide runs NLTK + the NumPy classifier for the live box; JavaScript shows four formats, the 10-step panel (progress in localStorage) and the rating form.
- **Netlify Forms** collects ratings; a **build hook** triggers rebuilds that fold ratings back in.
- Netlify Functions support TypeScript, JavaScript and Go only, so there is no Python at request time.
- Pyodide's package list includes nltk, numpy and scikit-learn but not spaCy.

## Sources
- docs/06-netlify-architecture.md (this repo)
- https://docs.netlify.com/functions/build/
- https://pyodide.org/en/stable/usage/packages-in-pyodide.html
