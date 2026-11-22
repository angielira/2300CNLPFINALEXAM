# VADER sentiment in NLTK

- `from nltk.sentiment.vader import SentimentIntensityAnalyzer`; `SentimentIntensityAnalyzer().polarity_scores(text)` returns `neg`, `neu`, `pos`, `compound`.
- Loads `sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt` by default.
- Sensitive to capitals, exclamation marks and degree words: in the NLTK how-to, "VADER is VERY SMART, handsome, and FUNNY!!!" scores higher (0.9342) than the plain sentence (0.8316).
- `compound` is normalized to -1..+1. Common thresholds: >= 0.05 positive, <= -0.05 negative.

## Limits to watch
Built for social media; misses domain negatives ("not working"), sarcasm and mixed messages.

## Sources
- https://www.nltk.org/howto/sentiment.html
- https://www.nltk.org/api/nltk.sentiment.vader.html
- https://www.nltk.org/_modules/nltk/sentiment/vader.html
