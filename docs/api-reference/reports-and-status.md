# Reports and Status

## `VerificationStatus`

`VerificationStatus` is a string-valued enum describing the logical conclusion
of one property.

```python
from toetra import VerificationStatus
```

| Member | Value | Meaning |
|---|---|---|
| `PROVED` | `"proved"` | No counterexample exists under the encoded assumptions |
| `COUNTEREXAMPLE` | `"counterexample"` | A concrete violation of a universal property was found |
| `WITNESS` | `"witness"` | A satisfying assignment for an existential property was found |
| `NO_WITNESS` | `"no_witness"` | No satisfying assignment exists under the encoded assumptions |
| `UNKNOWN` | `"unknown"` | Execution or policy could not support a logical conclusion |

Status interpretation depends on the property's verification semantics.
`PROVED` and `WITNESS` are positive conclusions; `COUNTEREXAMPLE` and
`NO_WITNESS` are failures for `VerificationSession.exit_code`.

Technical termination is reported separately. A timeout, cancellation or
resource limit must not be presented as a stronger logical result and normally
produces `UNKNOWN` with backend-execution evidence explaining why.

```python
if report.status is VerificationStatus.UNKNOWN:
    execution = report.backend_execution
    print(execution.status if execution is not None else "no execution evidence")
```

## `VerificationReport`

`VerificationReport` is the backend-neutral, user-facing record of one
completed property. Obtain reports from `session.reports` or
`finding.report`; application code should not construct them directly.

### Core fields

| Field | Meaning |
|---|---|
| `property_index` | Zero-based property position in the source |
| `property_type` | Toetra property family |
| `semantics` | Refutation or witness interpretation used for the property |
| `scope` | Normalized quantifier and declared variables |
| `specification` | Concise source-level property |
| `backend` | Selected backend |
| `backend_status` | Native backend status text |
| `status` | Public `VerificationStatus` |
| `summary` | User-facing conclusion summary |
| `assignments` | Normalized backend assignments |
| `diagnostics` | Structured diagnostics |
| `assumption_count` | Number of encoded assumptions |
| `route_reason` | Why the backend route was selected |
| `points` | Evidence grouped by semantic point |
| `numeric_compatibility` | Numeric route and permitted-conclusion evidence |
| `backend_execution` | Termination status, duration and applied limits |
| `provenance` | Versioned artifact and verification fingerprints |
| `model_evaluations` | Output-observable and lowering evidence |

The report also retains normalized assignments and point evidence. Values
exposed through convenience dictionaries use normal Python scalar types.

### Assignment views

| Property | Meaning |
|---|---|
| `inputs` | Input assignment objects |
| `outputs` | Scalar model-output assignment objects |
| `auxiliary_assignments` | Internal quantities and backend-introduced assignments |
| `qualified_input_values` | Inputs keyed by qualified Toetra name |
| `point_values` | Input dictionaries grouped by semantic point |
| `output_values_by_point` | Output dictionaries grouped by semantic point |
| `model_evaluations_by_point` | Classification/output-observable evidence grouped by point |
| `input_values` | Unqualified input dictionary for one unambiguous point |
| `output_values` | Output dictionary for one unambiguous point |

`input_values` and `output_values` raise `ValueError` for multi-point evidence.
This prevents pairwise assignments from being flattened silently.

Classification labels and probabilities live in `model_evaluations`; they are
not forced into the scalar `outputs` collection.

### Outcome helper

`has_failure` is `True` only for `COUNTEREXAMPLE`. It is a report-level
violation helper and therefore differs from `VerificationSession.has_failures`,
which also includes `NO_WITNESS`.

### Rendering and JSON

```python
report.to_text() -> str
report.to_html() -> str
report.to_dict() -> dict
report.to_json(*, indent=2) -> str
report.write_json(path, *, indent=2) -> Path
report.write_html(path) -> Path
```

```python
text = report.to_text()
html = report.to_html()

payload = report.to_dict()
json_text = report.to_json(indent=2)

json_path = report.write_json("artifacts/property-1.json")
html_path = report.write_html("artifacts/property-1.html")
```

The write methods create missing parent directories and return the written
`Path`. Notebook display delegates to `to_html()`.

`to_dict()`, `to_json()` and `write_json()` use:

```text
toetra.verification-report / schema_version 6
```

Session-level JSON uses the separate
`toetra.verification-report-collection` envelope. JSON compatibility is
governed by the [output reporting contract](../contracts/output-reporting-and-replay.md),
not by the shape of `to_records()`.

### Trust boundary

A report records the semantic target and conclusion scope of the selected
numeric route. A `PROVED` status over an exact-real affine encoding must not be
read as a silent claim of bit-exact framework execution. Inspect:

```python
compatibility = report.numeric_compatibility
if compatibility is not None:
    print(compatibility.classification)
    print(compatibility.semantic_target)
    print(compatibility.conclusion_scope)
```

Concrete replay checks returned evidence against a model instance, but does not
widen that formal conclusion.
