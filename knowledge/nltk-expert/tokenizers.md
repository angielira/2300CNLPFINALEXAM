# NLTK tokenizers

- `word_tokenize(text, language='english', preserve_line=False)`: improved Treebank tokenizer plus Punkt sentence splitting; requires the Punkt models. Example output keeps `$` and `3.88` as tokens.
- `sent_tokenize(text, language='english')`: PunktSentenceTokenizer for the language.
- `wordpunct_tokenize(text)`: regex split on whitespace and punctuation (splits `3.88` into `3`, `.`, `88`).
- `RegexpTokenizer(pattern)`: custom regex; needs no data files (good for Pyodide).
- `TweetTokenizer` / `casual_tokenize`: for informal text with emoticons.

## HelpMate choice
Use `RegexpTokenizer(r"[A-Za-z0-9']+")` in both build and browser so results match and no Punkt data is needed.

## Sources
- https://www.nltk.org/api/nltk.tokenize.html
