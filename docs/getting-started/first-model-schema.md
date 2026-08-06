# First model schema

> **Status:** Current onboarding for `1.0.0rc4`
>
> **Audience:** users who need to understand how a model becomes verifiable

`ModelSchema` is Toetra's normalized, framework-independent description of a
model interface. Normal users pass a fitted model artifact and an optional
reference dataset to `verify(...)`; the runtime loads, detects, and introspects
the model before building the schema.

```text
model artifact + optional dataset + selected output
→ loader → framework detector → introspector
→ ModelSchema
→ schema-aware semantic validation and model encoding
```

`ModelSchema` is an internal compiler boundary, not one of the nine public names
exported by `toetra`.

## What the schema records

| Field | Meaning |
|---|---|
| framework | normalized framework identity |
| model type | concrete estimator family detected by the adapter |
| features | ordered names, semantic dtypes, nullability, and source dtypes |
| output name | selected model output port |
| task | regression, classification, or unknown |
| typed output schema | public observables and their types |
| compatibility descriptor | framework/model numeric semantics used for routing |
| metadata | adapter-specific evidence that does not define generic semantics |

Regression exposes one scalar value. The direct binary-logistic route exposes
the predicted label and label-keyed probabilities together with its recognized
native decision policy.

## Why Toetra needs it

For a property such as:

```toetra
[LOGIC]:
forall applicant
with domain(applicant.income: [3.0, 6.0])
=> target[applicant].probability("yes") >= 0.80 using Z3
```

the schema lets semantic validation establish that:

- `income` is a known numeric feature;
- the selected output is a classifier output;
- `"yes"` is one of the two canonical labels;
- class probability is an available observable;
- the framework/model pair has a compatible formal encoder.

The schema does not itself prove the property. Model-family semantics lower the
public observable, the encoder contributes model equations as IR2 assumptions,
and the selected backend executes the resulting verification task.

## Public V1 routes

| Model artifact | Typed output | Formal route |
|---|---|---|
| fitted single-output sklearn `LinearRegression` | scalar regression value | affine equation → Z3 |
| direct fitted binary sklearn `LogisticRegression` | label and class probabilities | oriented affine decision equation → Z3 |

Detection or introspection code for another framework is not an end-to-end
support claim. The [public V1 profile](../public-v1-profile.md) remains the
authority for executable routes.

## Supplying inputs

The normal public workflow uses a model artifact:

```python
from toetra import verify

session = verify(
    "policy.toetra",
    model="model.joblib",
    dataset="reference.csv",
)
```

Advanced development hooks can inject an explicit schema, encoder factory, or
registry, but their accepted types live below private `toetra._*` modules and
carry no public compatibility guarantee.

## Boundaries

`ModelSchema` does not:

- reconstruct an sklearn `Pipeline`;
- make XGBoost, PyTorch, TensorFlow, or ONNX publicly supported;
- encode trees, ensembles, neural networks, or multiclass behavior;
- choose a backend by itself;
- replace reporting, provenance, or concrete replay.

Continue with the [ModelBridge overview](../model-bridge/overview.md), the
[as-built schema reference](../model-bridge/model-schema.md), and
[supported framework/model routes](../model-bridge/supported-frameworks.md).
