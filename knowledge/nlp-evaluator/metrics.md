# Metrics

- Accuracy plus per-class precision, recall and F1 (`classification_report`); macro average treats classes equally.
- Confusion matrix (`confusion_matrix`) shows which categories get mixed up.
- Use a stratified held-out split with a fixed `random_state`.

## Sources
- https://scikit-learn.org/stable/modules/model_evaluation.html
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html
