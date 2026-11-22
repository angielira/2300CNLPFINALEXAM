# 1. What NLTK does best for HelpMate

**Role in the app:** NLTK handles the *live, lightweight* language work (it runs in the browser through Pyodide) and the *statistics* over all questions and reviews at build time.

| HelpMate feature | NLTK tool | Where it runs |
|---|---|---|
| Clean up the user's question | `word_tokenize` / `RegexpTokenizer`, lower-casing | Browser (Pyodide) and build |
| Drop filler words ("my", "the", "is") | `nltk.corpus.stopwords.words("english")` | Browser and build |
| Detect frustration in a question | VADER `SentimentIntensityAnalyzer.polarity_scores()` | Browser |
| Score rating comments | VADER | Build (feedback loop) |
| Most common problems | `FreqDist` over cleaned tokens | Build |
| Common problem phrases ("blue screen", "forgot password") | `BigramCollocationFinder` + `BigramAssocMeasures.likelihood_ratio` / PMI | Build |
| Normalize word forms for keyword matching | `WordNetLemmatizer` or `PorterStemmer` | Browser and build |

## Frustration detection with VADER

- `SentimentIntensityAnalyzer().polarity_scores(text)` returns `neg`, `neu`, `pos` and a `compound` score from -1 (most negative) to +1 (most positive). ([NLTK sentiment how-to](https://www.nltk.org/howto/sentiment.html), [API](https://www.nltk.org/api/nltk.sentiment.vader.html))
- VADER reacts to capital letters, exclamation marks and intensifiers ("VERY", "!!!"), which is exactly how frustrated non-technical users write. The NLTK how-to shows the score rising as the same sentence gets more capitals and exclamation marks.
- Common thresholds from the literature: compound ≥ 0.05 positive, ≤ -0.05 negative, otherwise neutral.
- **HelpMate rule (proposed):** compound ≤ -0.4 → "frustrated" → switch to the calm tone, shorter steps and a reassurance line. Tune the cut-off on real examples and report the errors.
- **Known limits to report:** VADER was built for social-media text. It misses negations of technical words ("the printer is not working" contains no strongly negative word) and sarcasm. Combine it with a small custom list of problem words (`not working`, `broken`, `crashed`, `again`) and report where it still fails.

## Data downloads

Build time: `nltk.download(["punkt_tab", "stopwords", "vader_lexicon", "wordnet"])` (punkt_tab replaces the older punkt resource in recent NLTK). In the browser `nltk.download()` should not be relied on: ship the needed data files with the site and point `nltk.data.path` at them (see `04-neural-network.md` and `06-netlify-architecture.md`).

## Why NLTK and not spaCy for these parts

NLTK is available as a Pyodide package (nltk 3.9.4 in Pyodide 314.0.8) while spaCy is not, so everything that must react *live* to the user's typing belongs to NLTK. ([Pyodide packages](https://pyodide.org/en/stable/usage/packages-in-pyodide.html))

## Sources
- NLTK sentiment how-to: https://www.nltk.org/howto/sentiment.html
- NLTK VADER API: https://www.nltk.org/api/nltk.sentiment.vader.html
- NLTK collocations how-to: https://www.nltk.org/howto/collocations.html
- NLTK data: https://www.nltk.org/data.html
- Pyodide package list: https://pyodide.org/en/stable/usage/packages-in-pyodide.html
