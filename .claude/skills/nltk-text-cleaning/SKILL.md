---
name: nltk-text-cleaning
description: "Clean and normalize text with NLTK: tokenize, lower-case, remove stopwords, lemmatize. Use for questions, tickets and comments, at build time or in Pyodide."
---

# nltk-text-cleaning

Used by: nltk-expert, ml-engineer, pyodide-engineer, build-pipeline-engineer

## Recipe
```python
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer

_TOKEN = RegexpTokenizer(r"[A-Za-z0-9']+")
_STOP = set(stopwords.words("english")) - {"not", "no", "won't", "can't", "isn't", "doesn't"}
_LEM = WordNetLemmatizer()

def clean(text: str) -> list[str]:
    tokens = _TOKEN.tokenize(text.lower())
    return [_LEM.lemmatize(t) for t in tokens if t not in _STOP]
```
- Keep negations: they carry the problem ("won't print").
- `RegexpTokenizer` needs no Punkt data, which makes it the safest choice in the browser. `word_tokenize` requires the Punkt models (`punkt_tab`).
- Data needed: `stopwords`, `wordnet` (and `omw-1.4` if the lemmatizer asks).
