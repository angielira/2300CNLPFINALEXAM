---
name: mlp-training
description: "Train and evaluate HelpMate's TF-IDF + MLPClassifier question classifier. Use when training or retraining the neural network."
---

# mlp-training

Used by: ml-engineer, feedback-loop-engineer

## Recipe
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=2000, sublinear_tf=True)
X = vec.fit_transform(texts)
Xtr, Xte, ytr, yte = train_test_split(X, labels, test_size=0.2, stratify=labels, random_state=42)
clf = MLPClassifier(hidden_layer_sizes=(64,), solver="lbfgs", alpha=1e-3, max_iter=500, random_state=42)
clf.fit(Xtr, ytr)
print(classification_report(yte, clf.predict(Xte)))
```
- For small datasets `lbfgs` often converges faster than the default `adam`.
- Always report on a held-out test set and on the plain-language seed set.
