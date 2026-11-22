# 4. The neural network: a question classifier that runs in the browser

**Goal:** route each question to one of 8 categories (Printer, Email, Wi-Fi/Internet, Passwords/Login, Computer slow, Phone/Apps, Files/Storage, Video calls) so HelpMate shows the right answer and mini-course.

## Design

| Step | Where | Details |
|---|---|---|
| Features | Build | TF-IDF over NLTK-cleaned tokens (`TfidfVectorizer`, unigrams + bigrams, ~2,000 features) |
| Model | Build | `sklearn.neural_network.MLPClassifier(hidden_layer_sizes=(64,), max_iter=500, random_state=42)` |
| Evaluation | Build | 80/20 split; accuracy, per-class precision/recall, confusion matrix → `reports/` |
| Export | Build | Save vocabulary, IDF weights, layer weights (`coefs_`) and biases (`intercepts_`) to `model.json` |
| Prediction | Browser (Pyodide) | Load `model.json`, build the TF-IDF vector, run the forward pass with NumPy (ReLU hidden layer, softmax output) |

## Why export weights to JSON instead of pickling

Pyodide does ship scikit-learn (1.8.0 in Pyodide 314.0.8), so loading a pickled model is possible, but a pickle only loads reliably with the *same* scikit-learn version it was saved with, and the scikit-learn wheel adds several MB to the first page load. A one-hidden-layer MLP is just two matrix multiplications, so NumPy alone (also in Pyodide) is enough and keeps the app fast. If the team prefers pickling, pin `scikit-learn==1.8.0` in `requirements.txt` to match Pyodide. ([Pyodide packages](https://pyodide.org/en/stable/usage/packages-in-pyodide.html))

## Honesty points for the report

- Report test accuracy on the **seed set** (plain-language questions), not only on formal tickets.
- Show 3–5 misclassified examples and why (e.g. "my email won't send from my phone" sits between Email and Phone/Apps).
- spaCy's `en_core_web_sm` is also a neural network, so the app uses two neural models: one off-the-shelf (spaCy) and one trained by the team (the MLP).

## Running Python in the browser (Pyodide basics)

- Load Pyodide from its CDN, then `await pyodide.loadPackage(["nltk", "numpy"])`.
- `nltk.download()` should not be used in the browser: copy `stopwords`, `vader_lexicon` and `punkt_tab` into the site at build time, fetch them, write them into Pyodide's virtual file system, and add that folder to `nltk.data.path`.
- First load takes a few seconds: show a friendly "Getting HelpMate ready…" message and cache with the browser.

## Sources
- scikit-learn MLPClassifier: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html
- scikit-learn model persistence: https://scikit-learn.org/stable/model_persistence.html
- Pyodide packages: https://pyodide.org/en/stable/usage/packages-in-pyodide.html
- Pyodide loading packages: https://pyodide.org/en/stable/usage/loading-packages.html
