---
name: nltk-text-cleaning
description: "Clean and normalize text with NLTK the HelpMate way: lower-case, RegexpTokenizer, stopwords minus negations, PorterStemmer. Use for questions, tickets and comments, at build time or in Pyodide."
---

# nltk-text-cleaning

Used by: nltk-expert, ml-engineer, pyodide-engineer, build-pipeline-engineer

Binding contract: `reports/plan.md` section 4.1. If anything here differs from the plan, the plan wins.

## Recipe (`nlp/nltk_features.py`)
Imports: nltk + stdlib only (no spaCy, no sklearn, no numpy), so the module imports in Pyodide.
```python
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer

NEGATIONS = frozenset({"no", "not", "nor", "never", "cannot"})   # plus any token ending in "n't"
TOKEN_PATTERN = r"[a-z0-9]+(?:'[a-z]+)?"
_TOKENIZER = RegexpTokenizer(TOKEN_PATTERN)
_STEMMER = PorterStemmer()
_STOP = None      # loaded lazily on first use, then cached
_LEM = None       # WordNetLemmatizer, build time only

def use_data_dir(path: str) -> None:
    nltk.data.path.insert(0, path)

def _stopwords() -> frozenset:
    global _STOP
    if _STOP is None:
        from nltk.corpus import stopwords
        _STOP = frozenset(stopwords.words("english"))
    return _STOP

def _keep(tok: str) -> bool:
    return tok in NEGATIONS or tok.endswith("n't") or tok not in _stopwords()

def tokenize(text: str) -> list[str]:
    return _TOKENIZER.tokenize(text.replace("’", "'").lower())

def clean(text: str) -> list[str]:          # build AND browser; used by the classifier ("nltk_clean_v1")
    return [_STEMMER.stem(t) for t in tokenize(text) if _keep(t)]

def lemmas(text: str) -> list[str]:         # BUILD ONLY (needs wordnet); used for nltk_stats.json
    global _LEM
    if _LEM is None:
        from nltk.stem import WordNetLemmatizer
        _LEM = WordNetLemmatizer()
    return [_LEM.lemmatize(t) for t in tokenize(text) if _keep(t)]
```

## Rules
- `clean()` uses **PorterStemmer**, which needs no data files. Only the stopword list is read from NLTK data.
- `lemmas()` uses WordNetLemmatizer and runs **only at build time**. WordNet is never shipped to the browser.
- Keep negations: they carry the problem ("won't print", "not working").
- Load stopwords (and VADER) lazily and cache them, so `import nlp.nltk_features` never needs data.
- `RegexpTokenizer` needs no Punkt data; do not use `word_tokenize` (it needs `punkt_tab`).
- Build and browser must use the same nltk version (3.9.4) so `clean()` gives identical tokens.

## NLTK data
- Build time (`.cache/nltk_data`): `stopwords`, `vader_lexicon`, `wordnet`, `omw-1.4`.
- Shipped to the browser (`site/nltk_data/`): only `corpora/stopwords/english` and `sentiment/vader_lexicon/vader_lexicon.txt`.
