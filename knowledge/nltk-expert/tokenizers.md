# NLTK tokenizers

- `word_tokenize(text, language='english', preserve_line=False)`: improved Treebank tokenizer plus Punkt sentence splitting; requires the Punkt models. Example output keeps `$` and `3.88` as tokens.
- `sent_tokenize(text, language='english')`: PunktSentenceTokenizer for the language.
- `wordpunct_tokenize(text)`: regex split on whitespace and punctuation (splits `3.88` into `3`, `.`, `88`).
- `RegexpTokenizer(pattern)`: custom regex; needs no data files (good for Pyodide).
- `TweetTokenizer` / `casual_tokenize`: for informal text with emoticons.

## Stemmer vs lemmatizer
- `PorterStemmer().stem(word)` (`nltk.stem.porter`): rule-based Porter algorithm; needs no data files.
- `WordNetLemmatizer().lemmatize(word)` (`nltk.stem.wordnet`): looks words up in WordNet; needs the `wordnet` data (and `omw-1.4`).

## HelpMate choice (binding: reports/plan.md section 4.1)
- In both build and browser: `text.replace("’", "'").lower()`, then `RegexpTokenizer(r"[a-z0-9]+(?:'[a-z]+)?")`, so results match and no Punkt data is needed.
- `clean()` drops English stopwords except negations (`no`, `not`, `nor`, `never`, `cannot`, any token ending in `n't`), then applies `PorterStemmer`. Used by the classifier in the build and in Pyodide.
- `lemmas()` uses the same filter with `WordNetLemmatizer` instead; build time only (nltk_stats.json). WordNet is never shipped to the browser.

## Sources
- https://www.nltk.org/api/nltk.tokenize.html
- https://www.nltk.org/api/nltk.stem.porter.html
- https://www.nltk.org/api/nltk.stem.wordnet.html
