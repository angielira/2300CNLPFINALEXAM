"""NLTK features for HelpMate (library label: NLTK).

Runs at build time AND in the browser (Pyodide). Imports: nltk + stdlib only.
Stopwords and VADER are loaded lazily, so importing this module needs no data.
Contract: reports/plan.md section 4.1.
"""
import re

import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer

LIBRARY = "NLTK"
NEGATIONS = frozenset({"no", "not", "nor", "never", "cannot"})  # tokens ending in "n't" are kept too
FRUSTRATION_THRESHOLD = -0.4
FRUSTRATION_PHRASES = (
    "not working", "doesn't work", "won't", "can't", "broken", "crashed",
    "again", "nothing works", "tried everything", "keeps", "stuck", "frozen",
)
TOKEN_PATTERN = r"[a-z0-9]+(?:'[a-z]+)?"
VADER_LEXICON_PATH = "sentiment/vader_lexicon/vader_lexicon.txt"

_TOKENIZER = RegexpTokenizer(TOKEN_PATTERN)
_STEMMER = PorterStemmer()
_STOP = None    # frozenset, loaded on first use
_LEM = None     # WordNetLemmatizer, build time only
_SIA = None     # SentimentIntensityAnalyzer, loaded on first use
_CAPS_RE = re.compile(r"\b[A-Z]{4,}\b")


def use_data_dir(path: str) -> None:
    """Make NLTK look for data (stopwords, vader_lexicon) in `path` first."""
    if path not in nltk.data.path:
        nltk.data.path.insert(0, path)


def _stopwords() -> frozenset:
    global _STOP
    if _STOP is None:
        from nltk.corpus import stopwords
        _STOP = frozenset(stopwords.words("english"))
    return _STOP


def _keep(tok: str) -> bool:
    return tok in NEGATIONS or tok.endswith("n't") or tok not in _stopwords()


def tokenize(text: str) -> list:
    return _TOKENIZER.tokenize(text.replace("’", "'").lower())


def clean(text: str) -> list:
    """Tokenizer "nltk_clean_v1": lower, tokenize, drop stopwords (keep negations), Porter stem."""
    return [_STEMMER.stem(t) for t in tokenize(text) if _keep(t)]


def lemmas(text: str) -> list:
    """Same filter as clean() but WordNet lemmas. BUILD ONLY (needs wordnet data)."""
    global _LEM
    if _LEM is None:
        from nltk.stem import WordNetLemmatizer
        _LEM = WordNetLemmatizer()
    return [_LEM.lemmatize(t) for t in tokenize(text) if _keep(t)]


def _analyzer():
    global _SIA
    if _SIA is None:
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        try:
            nltk.data.find(VADER_LEXICON_PATH)
            _SIA = SentimentIntensityAnalyzer(lexicon_file=VADER_LEXICON_PATH)
        except LookupError:
            _SIA = SentimentIntensityAnalyzer()   # default: sentiment/vader_lexicon.zip
    return _SIA


def _has_phrase(text_lower: str) -> bool:
    for p in FRUSTRATION_PHRASES:
        if re.search(r"(?<![a-z0-9'])" + re.escape(p) + r"(?![a-z0-9'])", text_lower):
            return True
    return False


def frustration(text: str) -> dict:
    scores = _analyzer().polarity_scores(text)
    norm = text.replace("’", "'")
    reasons = []
    if scores["compound"] <= FRUSTRATION_THRESHOLD:
        reasons.append("vader_negative")
    if _has_phrase(norm.lower()):
        if "!!" in norm:
            reasons.append("problem_phrase+exclaim")
        elif _CAPS_RE.search(norm):
            reasons.append("problem_phrase+caps")
    return {
        "neg": scores["neg"], "neu": scores["neu"], "pos": scores["pos"],
        "compound": scores["compound"],
        "frustrated": bool(reasons), "reasons": reasons, "library": LIBRARY,
    }


def satisfaction(text: str) -> dict:
    """Score a rating comment: positive / neutral / negative (cut-offs +/-0.05)."""
    c = _analyzer().polarity_scores(text)["compound"]
    label = "positive" if c >= 0.05 else "negative" if c <= -0.05 else "neutral"
    return {"compound": c, "label": label}


def top_words(token_lists: list, n: int = 25) -> list:
    fd = nltk.FreqDist(t for toks in token_lists for t in toks)
    return [{"word": w, "count": c} for w, c in fd.most_common(n)]


def top_phrases(token_lists: list, n: int = 20, min_freq: int = 3) -> list:
    from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
    finder = BigramCollocationFinder.from_documents([list(t) for t in token_lists])
    finder.apply_freq_filter(min_freq)
    scored = finder.score_ngrams(BigramAssocMeasures().likelihood_ratio)[:n]
    return [{"phrase": " ".join(bg), "count": int(finder.ngram_fd[bg]), "score": round(float(s), 2)}
            for bg, s in scored]
