# Evaluation metrics

- `train_test_split(..., stratify=y, random_state=42)` keeps class balance.
- `classification_report(y_true, y_pred)`: precision, recall, F1 per class plus macro/weighted averages.
- `confusion_matrix(y_true, y_pred, labels=classes)`.

## Sources
- https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
