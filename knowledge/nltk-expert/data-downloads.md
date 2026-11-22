# NLTK data

- `nltk.download()` opens the downloader; `nltk.download('stopwords')` fetches one package.
- Command line: `python -m nltk.downloader -d <dir> stopwords vader_lexicon wordnet`; with `-d`, set `NLTK_DATA` to match.
- Manual install: create `nltk_data/` with subfolders (`corpora`, `sentiment`, `tokenizers`, ...) and unzip packages there; point `NLTK_DATA` at it.
- In code, `nltk.data.path` is the list of folders NLTK searches; prepend a folder to use shipped data.

## HelpMate packages
- Build time (downloaded to `.cache/nltk_data`): `stopwords`, `vader_lexicon`, `wordnet` (+ `omw-1.4`). HelpMate does not use `word_tokenize`, so `punkt_tab` is not needed.
- Shipped to the browser (`site/nltk_data/`, listed in nltk_manifest.json): only `corpora/stopwords/english` and `sentiment/vader_lexicon/vader_lexicon.txt`. WordNet stays at build time (see reports/plan.md section 4.5).

## Sources
- https://www.nltk.org/data.html
- https://www.nltk.org/api/nltk.data.html
