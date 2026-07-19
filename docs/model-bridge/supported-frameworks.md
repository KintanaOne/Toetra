# Supported frameworks and model families

The ModelBridge architecture is framework-neutral, but public support is declared
per complete framework/model/encoder/backend route.

## Built-in V1 support

| Framework | Model family | Loading/introspection | Model encoding | Backend route | End-to-end |
|---|---|---:|---:|---:|---:|
| scikit-learn | single-output `LinearRegression` | yes | affine equation | Z3 exact-real profile | yes |
| scikit-learn | other estimators | partial metadata may exist | no built-in V1 encoder | none | no |
| XGBoost | metadata/introspection experiments | partial | no | none | no |
| PyTorch | extension architecture only | no built-in V1 adapter | no | none | no |
| TensorFlow/Keras | extension architecture only | no built-in V1 adapter | no | none | no |
| ONNX | future framework-neutral representation | no built-in V1 adapter | no | none | no |

Detection or schema introspection alone does not constitute verification support.
A model is end-to-end supported only when loading, normalized schema, semantic
validation, model constraints, numeric compatibility, backend capabilities,
execution, reports, and tests all agree.

## V1 sklearn restrictions

- fitted `LinearRegression`;
- regression task;
- one output and one declared target;
- finite numeric coefficients, intercept, features, domains, and anchors;
- feature order consistent with the fitted model/schema;
- transformed model inputs rather than reconstructed raw preprocessing.

The generated numeric compatibility matrices are the runtime-derived source for
registered framework/model/backend routes.
