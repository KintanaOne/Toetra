# Replay and Errors

## `CounterexampleReplay`

Despite its historical name, `CounterexampleReplay` is the public replay result
returned by `VerificationFinding.replay(...)` for replayable formal evidence.
It compares the formal assignment with observations from a concrete model.

```python
from toetra import CounterexampleReplay

finding = session.first_counterexample
if finding is not None:
    replay: CounterexampleReplay = finding.replay(tolerance=1e-9)
```

Replay requires:

- a model attached by artifact-based `verify(...)`, or a model passed directly
  to `finding.replay(model=...)`;
- a property that references a model output;
- complete input evidence for every referenced point;
- a runtime observer capable of evaluating the model.

If any requirement is missing, replay raises `ReplayUnavailableError` instead
of returning partial evidence.

### Evidence by point

| Property | Meaning |
|---|---|
| `property_index` | Zero-based source property index |
| `points` | Replay evidence keyed by semantic point |
| `inputs_by_point` | Concrete input dictionaries by point |
| `backend_outputs_by_point` | Formally assigned outputs by point |
| `model_outputs_by_point` | Concretely observed outputs by point |
| `relation_satisfied` | Concrete scope restriction result, or `None` |
| `assertion_satisfied` | Concrete property result, or `None` |
| `expected_assertion_satisfied` | Expected result derived from the formal status |
| `tolerance` | Absolute comparison tolerance |
| `max_absolute_error` | Largest available formal/concrete numeric difference |

The `inputs`, `backend_outputs`, `model_outputs` and `absolute_errors`
conveniences are available only for single-point replay. They raise
`ValueError` for multi-point evidence; use the corresponding `*_by_point`
property or inspect `points`.

### Consistency

| Property | Meaning |
|---|---|
| `assertion_consistent` | Concrete assertion does not contradict the expected formal result |
| `relation_consistent` | Concrete point remains compatible with its scope restriction |
| `is_consistent` | All available output/evaluation errors are within tolerance and both logical checks are consistent |

A comparison inside the configured tolerance band around an ordering boundary
may be indeterminate (`None`). Indeterminate is not treated as a contradiction.

Replay validates concrete evidence only. It does not turn a result scoped to a
formal encoding into a proof about bit-exact source-model execution.

The tolerance must be finite and non-negative. Invalid values raise
`ValueError`.

### Rendering and records

```python
replay.to_records() -> list[dict]
replay.to_record() -> dict
replay.to_dataframe()
replay.to_text() -> str
replay.to_html() -> str
```

```python
print(replay.to_text())
html = replay.to_html()

records = replay.to_records()
frame = replay.to_dataframe()
```

`to_records()` returns one record per point. `to_record()` is the single-point
convenience and raises `ValueError` for multi-point replay. Notebook display
delegates to `to_html()`.

## Public error hierarchy

```text
RuntimeError
└── VerificationRuntimeError
    ├── VerificationConfigurationError
    └── ReplayUnavailableError
```

Other internal subclasses may also be raised as
`VerificationRuntimeError`, but their concrete classes are not part of the
public facade.

### `VerificationRuntimeError`

Base class for user-facing runtime orchestration errors. Catch it when the
caller can handle any public runtime failure uniformly:

```python
from toetra import VerificationRuntimeError, verify

try:
    session = verify("policy.toetra", model="model.joblib")
except VerificationRuntimeError as error:
    print(f"{error.code} at {error.stage}: {error}")
```

All three public error families expose:

| Attribute | Meaning |
|---|---|
| `message` | human-readable summary, also returned by `str(error)` |
| `code` | stable programmatic diagnostic identifier |
| `stage` | owning failure stage |
| `hint` | optional remediation |
| `path` | optional source or artifact path |
| `line`, `column` | optional one-based source location |

Message wording may improve. Callers that need stable branching use `code`.
When Toetra normalizes a private compiler, model, or backend failure, its
original exception remains available through `error.__cause__`.

Syntax, CST-to-AST construction, and semantic-validation failures are
normalized by `verify(...)` as `VerificationConfigurationError` while
retaining `syntax`, `builder`, or `semantic` ownership. Model, compatibility,
routing, and backend normalization continues in later P26 steps; failures from
those still-unfinished boundaries may still cross `verify(...)` directly.

### `VerificationConfigurationError`

Raised when runtime inputs are ambiguous or inconsistent, including:

- malformed specification syntax;
- a CST shape that cannot be represented as a Toetra AST;
- invalid binding, typing, domain, property, or output-observable semantics;
- mixing `schema` with `model` or `dataset`;
- target disagreement between arguments, schema and specification;
- providing both `anchor_source` and `anchor_resolver`;
- using a retired specification extension.

It inherits from both `VerificationRuntimeError` and `ValueError`.

### `ReplayUnavailableError`

Raised when Toetra cannot replay formal evidence completely, including:

- no concrete model is attached or supplied;
- the property does not reference a model output;
- required point features or formal outputs are absent;
- no runtime observer supports the model;
- a required label, probability or model quantity is unavailable.

Replay never silently drops a point or observable.
