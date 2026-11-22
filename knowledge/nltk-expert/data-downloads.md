# NLTK data

- `nltk.download()` opens the downloader; `nltk.download('stopwords')` fetches one package.
- Command line: `python -m nltk.downloader -d <dir> stopwords vader_lexicon wordnet`; with `-d`, set `NLTK_DATA` to match.
- Manual install: create `nltk_data/` with subfolders (`corpora`, `sentiment`, `tokenizers`, ...) and unzip packages there; point `NLTK_DATA` at it.
- In code, `nltk.data.path` is the list of folders NLTK searches; prepend a folder to use shipped data.

## HelpMate packages
`stopwords`, `vader_lexicon`, `wordnet` (+ `omw-1.4`), `punkt_tab` only if `word_tokenize` is used.

## Sources
- https://www.nltk.org/data.html
- https://www.nltk.org/api/nltk.data.html
