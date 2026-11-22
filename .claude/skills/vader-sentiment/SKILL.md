---
name: vader-sentiment
description: "Score text with NLTK VADER for frustration (questions) and satisfaction (rating comments). Use whenever HelpMate needs sentiment."
---

# vader-sentiment

Used by: nltk-expert, feedback-loop-engineer, nlp-evaluator

## Recipe
```python
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()          # needs vader_lexicon
s = sia.polarity_scores("I've tried EVERYTHING and nothing works!!")
# {'neg': ..., 'neu': ..., 'pos': ..., 'compound': -1..+1}
```
- Standard thresholds: compound >= 0.05 positive, <= -0.05 negative, otherwise neutral.
- HelpMate frustration rule: compound <= -0.4 OR a problem phrase from `nlp/frustration_phrases.txt` plus `!!`/ALL CAPS.
- VADER boosts for capitals, `!` and intensifiers; it misses technical negatives ("not working") and sarcasm. Record misses for the evaluator.
