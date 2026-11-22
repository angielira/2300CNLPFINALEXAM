# TfidfVectorizer

- Equivalent to CountVectorizer + TfidfTransformer.
- Key params: `ngram_range` (default (1,1)), `max_features`, `min_df`, `max_df`, `sublinear_tf` (1+log tf), `norm='l2'`, `smooth_idf=True`, `lowercase=True`, `token_pattern=r"(?u)\b\w\w+\b"`.
- Attributes: `vocabulary_` (term -> column), `idf_`; `get_feature_names_out()`.
- Smoothed idf: `idf(t) = ln((1+n)/(1+df(t))) + 1`; rows are L2-normalized.

## Sources
- https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting
