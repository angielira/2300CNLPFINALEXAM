# MLPClassifier

- Multi-layer perceptron optimizing log-loss with LBFGS or SGD/Adam.
- Defaults: `hidden_layer_sizes=(100,)`, `activation='relu'`, `solver='adam'`, `alpha=0.0001`, `max_iter=200`.
- Small datasets: `lbfgs` can converge faster and perform better.
- `random_state` makes runs reproducible; `early_stopping=True` holds out 10% for validation.
- Attributes for export: `coefs_` (weight matrices), `intercepts_` (biases), `classes_`, `out_activation_`.
- Methods: `fit`, `predict`, `predict_proba`, `score`, `partial_fit`.

## Sources
- https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html
