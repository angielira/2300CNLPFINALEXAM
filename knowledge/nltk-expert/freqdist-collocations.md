# FreqDist and collocations

- `FreqDist(tokens).most_common(n)` counts tokens.
- `BigramCollocationFinder.from_words(tokens)` builds candidates; `apply_freq_filter(3)` drops rare pairs; `apply_word_filter(fn)` drops pairs with unwanted words.
- `finder.nbest(BigramAssocMeasures().pmi, 10)` returns top pairs; `score_ngrams(measure)` returns pairs with scores.
- Measures: `pmi`, `likelihood_ratio`, `chi_sq`, `raw_freq`.

## Sources
- https://www.nltk.org/howto/collocations.html
- https://www.nltk.org/api/nltk.probability.FreqDist.html
