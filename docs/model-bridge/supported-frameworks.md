# Supported frameworks and model families

Public support is declared per complete framework/model/semantic-profile/backend
route.

| Framework | Model family | Encoding | Backend | End-to-end |
|---|---|---|---|---:|
| scikit-learn | fitted single-output `LinearRegression` | affine output | Z3 | yes |
| scikit-learn | direct fitted binary `LogisticRegression` | affine oriented decision | Z3 | yes |
| scikit-learn | other estimators/wrappers | no public encoder | none | no |
| XGBoost/PyTorch/TensorFlow/ONNX | extension or experiments | no public route | none | no |

The binary route accepts exactly two classes, one output, finite numeric features
and parameters, deterministic labels, and the native strict `p > 0.5` policy. It
rejects multiclass estimators, pipelines, `FixedThresholdClassifier`,
`TunedThresholdClassifierCV`, `CalibratedClassifierCV`, custom wrappers, and
custom thresholds before backend execution.

```text
LinearRegression   → target[point]
LogisticRegression → target[point].label
LogisticRegression → target[point].probability(label)
```

The internal oriented decision value is not a DSL observable. Generated numeric
compatibility matrices are the runtime-derived guarantee source.
