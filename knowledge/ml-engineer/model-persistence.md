# Saving models

- pickle/joblib/cloudpickle can execute arbitrary code on load; only load trusted files.
- Use the same scikit-learn and dependency versions for saving and loading; cross-version loading is unsupported (`InconsistentVersionWarning`).
- ONNX serves predictions without Python; skops.io is a safer object format.

## HelpMate choice
Export weights and vocabulary to JSON and predict with NumPy: version-independent and safe.

## Sources
- https://scikit-learn.org/stable/model_persistence.html
