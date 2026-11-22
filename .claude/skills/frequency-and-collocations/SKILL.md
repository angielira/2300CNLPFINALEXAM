---
name: frequency-and-collocations
description: "Find the most common problem words and phrases with NLTK FreqDist and bigram collocations. Use for build-time stats and the Insights page."
---

# frequency-and-collocations

Used by: nltk-expert, data-viz-expert

## Recipe
```python
from nltk import FreqDist
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures

fd = FreqDist(tokens)                       # tokens from nltk-text-cleaning
top_words = fd.most_common(25)

finder = BigramCollocationFinder.from_words(tokens)
finder.apply_freq_filter(3)                 # drop rare pairs
bm = BigramAssocMeasures()
top_phrases = finder.nbest(bm.likelihood_ratio, 20)
```
- `pmi` favors rare pairs; `likelihood_ratio` is more stable on small data.
- Write results to `site/data/nltk_stats.json` with a `"library": "NLTK"` field.
