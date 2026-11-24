# HelpMate research (docs index)

**HelpMate** is a friendly self-help IT coach for non-technical users. A user types an IT question in plain words; the app finds the device or app and the problem, notices frustration, and gives step-by-step help in the format they choose (See it, Hear it, Try it, Read it). An optional 10-step mini-course tracks their learning, and ratings make the app better on every rebuild.

This folder is the shared context for the agent team built next.

| # | File | Answers |
|---|---|---|
| 1 | [01-nltk.md](01-nltk.md) | What NLTK does best here: tokenizing, stopwords, VADER frustration and comment sentiment, FreqDist, collocations |
| 2 | [02-spacy.md](02-spacy.md) | What spaCy does best here: EntityRuler for devices/apps/error codes, dependency parse for the problem, noun chunks and lemmas |
| 3 | [03-dataset.md](03-dataset.md) | Which free dataset to use, its license, and the plain-language seed set |
| 4 | [04-neural-network.md](04-neural-network.md) | The MLP question classifier: trained at build time, run in the browser |
| 5 | [05-learning-formats.md](05-learning-formats.md) | What research says about learning styles (VARK) and how HelpMate offers formats responsibly |
| 6 | [06-netlify-architecture.md](06-netlify-architecture.md) | What Netlify can and cannot run, the recommended architecture, and the self-improvement loop |
| 7 | [expert-roster.md](expert-roster.md) | The 19-agent team (including product manager, software architect and security reviewer), who covers DevOps and back-end work, and the shared skills |
| 8 | [agent-brains.md](agent-brains.md) | Each agent's name, model and personality |

## Key findings

1. **Netlify runs Python only at build time.** Functions support TypeScript, JavaScript and Go, not Python.
2. **Pyodide runs NLTK, NumPy and scikit-learn in the browser, but not spaCy.** So spaCy runs at build time and saves JSON; NLTK and the neural network power the live question box.
3. **Ratings use Netlify Forms; progress uses localStorage.** No database or backend server is needed.
4. **The app improves on each rebuild:** new ratings are scored with VADER, answers are re-ranked and the classifier is retrained.
5. **Learning styles:** people have format preferences, but matching instruction to a "style" is not supported by evidence, so HelpMate lets users choose and switch formats freely.

## Brand

Logo files in `assets/brand/`. Colors: navy #14213D, blue #2F7BF5 (See it), coral #FF6A4D (Hear it), teal #12A889 (Try it), purple #8A5CF6 (Read it), background #FFF8F0. Font: Nunito.

_Research compiled November 2026._
