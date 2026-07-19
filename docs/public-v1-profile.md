# Public V1 profile

> Release candidate: `1.0.0rc1`  
> Contract date: 2026-07-19

This page is the public source of truth for what FORML V1 supports. Architecture
and vocabulary may describe future extension points, but they do not expand this
profile.

## Supported end-to-end route

| Axis | V1 support |
|---|---|
| Python | 3.11 and 3.12 |
| Framework | scikit-learn |
| Model | fitted, single-output `LinearRegression` |
| Inputs | finite transformed numeric features |
| Output | one finite numeric regression target |
| Model encoding | affine equation per requested point evaluation |
| Bindings | homogeneous `forall` chains or homogeneous `exists` chains |
| Points | inline anchors, referenced anchors, dataset fallback |
| Domains | numeric intervals, open/closed bounds, finite numeric sets |
| Expressions | constants, feature/output references, affine arithmetic, Boolean logic, comparisons |
| Neighborhood | implemented numeric-affine `Linf` restrictions where accepted by semantic lowering |
| Backend | Z3 |
| Results | `PROVED`, `COUNTEREXAMPLE`, `WITNESS`, `NO_WITNESS`, `UNKNOWN` |
| Evidence | grouped point assignments and real-estimator replay |
| Reports | text, HTML, Jupyter, records, DataFrame, JSON v5 |

## Numeric meaning

The default source model executes with framework floating-point semantics. The
built-in affine encoder and Z3 profile reason over an exact real-valued
abstraction. This route is intentionally registered as:

```text
classification: LOSSY
semantic target: forml.real_affine_extracted_model
conclusion scope: semantic_target_only
```

A `PROVED` result proves the property for that declared abstraction. It is not a
bit-exact proof of every floating-point operation performed by sklearn. Reports
preserve this distinction.

## Unsupported by the built-in profile

- classifiers, multi-output regressors, trees, ensembles, neural networks;
- nonlinear or symbolic-division model encodings;
- preprocessing reconstruction and raw-data-to-model symbolic pipelines;
- non-finite numeric values;
- categorical and string backend reasoning;
- alternating quantifier execution;
- multiple models or multiple targets in one property;
- built-in ERAN, MILP, abstract-interpretation, or remote backends;
- distributed campaigns, registries, dashboards, and governance workflows.

## Extension rule

A framework/model/backend combination is not public support merely because an
adapter can be registered. A supported extension must provide:

1. deterministic framework and model descriptors;
2. a ModelBridge encoder and semantic target;
3. backend capabilities and execution capabilities;
4. a numeric compatibility rule with permitted conclusions;
5. reporting and provenance evidence;
6. unit, contract, and end-to-end tests.

The generated matrices expose the currently registered rules without making any
framework or backend the architecture itself.
