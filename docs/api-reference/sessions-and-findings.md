# Sessions and Findings

## `VerificationSession`

`VerificationSession` is the complete result of one successful
[`verify(...)`](verify.md) invocation.

```python
from toetra import VerificationSession, verify

session: VerificationSession = verify(
    "policy.toetra",
    model="model.joblib",
)
```

One session retains the source, resolved artifact paths, normalized model
schema, provenance and one completed execution per property. Applications
normally consume `reports` or `findings`.

### Result collections

| Property | Type | Meaning |
|---|---|---|
| `reports` | `tuple[VerificationReport, ...]` | Stable user-facing reports in source order |
| `findings` | `tuple[VerificationFinding, ...]` | Ergonomic property views in source order |
| `results` | tuple | Backend-neutral execution results for diagnostics |
| `proved` | `tuple[VerificationFinding, ...]` | Findings with status `PROVED` |
| `counterexamples` | `tuple[VerificationFinding, ...]` | Findings with status `COUNTEREXAMPLE` |
| `witnesses` | `tuple[VerificationFinding, ...]` | Findings with status `WITNESS` |
| `no_witnesses` | `tuple[VerificationFinding, ...]` | Findings with status `NO_WITNESS` |
| `unknown` | `tuple[VerificationFinding, ...]` | Findings with status `UNKNOWN` |
| `first_counterexample` | `VerificationFinding \| None` | First counterexample, if present |
| `first_witness` | `VerificationFinding \| None` | First witness, if present |

`VerificationSession` is also a read-only sequence. Its items are lower-level
execution records whose class is not part of the nine-name public facade.
Application code that needs a stable public object should iterate over
`session.reports` or `session.findings`.

### Aggregate outcome

| Property | Definition |
|---|---|
| `is_successful` | At least one report exists and every status is `PROVED` or `WITNESS` |
| `has_failures` | At least one status is `COUNTEREXAMPLE` or `NO_WITNESS` |
| `has_unknown` | At least one status is `UNKNOWN` |
| `exit_code` | `1` for a failure, otherwise `2` for unknown, otherwise `0` |

A counterexample takes precedence over an unknown result in `exit_code`.

```python
session.print()
raise SystemExit(session.exit_code)
```

`exit_code` is an automation convention, not a replacement for inspecting
individual statuses and their semantic scope.

### Session metadata

The session exposes:

- `source`: compiled specification source;
- `specification_path`: resolved path or `None` for inline source;
- `executions`: lower-level execution records in property order;
- `model_path` and `dataset_path`: resolved artifact paths when loaded;
- `schema`: normalized schema used for compilation;
- `model`: attached concrete model, if loaded from artifacts;
- `provenance`: session-level provenance context;
- `anchor_resolutions`: resolved anchor evidence.

Some value types behind these attributes are private implementation models.
They are available for inspection but are not separate public construction or
extension contracts.

### Rendering and serialization

```python
session.to_records() -> list[dict]
session.to_dataframe()
session.to_text(*, options=None) -> str
session.print(*, file=None, options=None) -> None
session.to_dict() -> dict
session.to_json(*, indent=2) -> str
session.write_json(path, *, indent=2) -> Path
session.to_html(*, options=None) -> str
session.write_html(path, *, options=None) -> Path
session.write_artifacts(
    directory,
    *,
    formats=("json", "html"),
    stem="toetra-verification-report",
) -> dict[str, Path]
```

Renderer option objects are internal in `1.0.0rc3`; normal callers should use
the defaults.

```python
text = session.to_text()
session.print()

records = session.to_records()
frame = session.to_dataframe()

payload = session.to_dict()
json_text = session.to_json(indent=2)
json_path = session.write_json("artifacts/report.json")

html = session.to_html()
html_path = session.write_html("artifacts/report.html")
```

`to_dict()`, `to_json()` and `write_json()` use the versioned report-collection
contract. `to_records()` instead returns one flat summary record per property
for tabular analysis; multi-point input and output evidence remains grouped in
the `points` and `outputs_by_point` fields.

Each record also contains JSON-compatible nested blocks named
`backend_execution`, `numeric_compatibility`, `provenance`, `point_evidence`,
`assignments`, `model_evaluations`, and `diagnostics`. These blocks preserve the
machine evidence that cannot be flattened safely. Frequently filtered values
such as `status`, `summary`, `route_reason`, execution limits, numeric
classification and fingerprints remain available as top-level record columns.

`to_records()` is intentionally not a versioned interchange schema. Use
`to_dict()` or JSON v6 for durable exchange and use records/DataFrame for
analysis.

The write methods create missing parent directories and return the written
`Path`.

`write_artifacts(...)` writes several formats together:

```python
written = session.write_artifacts(
    "artifacts",
    formats=("json", "html"),
    stem="credit-policy",
)
# {"json": Path(...), "html": Path(...)}
```

Supported formats are `json` and `html`. Matching is case-insensitive,
duplicates are removed, and any unsupported format raises `ValueError`.

## `VerificationFinding`

`VerificationFinding` is a focused public view of one report plus the compiled
context required for replay.

```python
from toetra import VerificationFinding

finding: VerificationFinding | None = session.first_counterexample
```

### Status and evidence

| Property | Meaning |
|---|---|
| `status` | The report's `VerificationStatus` |
| `input_values` | Unqualified inputs when exactly one point is present |
| `qualified_input_values` | Inputs keyed by qualified Toetra names |
| `output_values` | Outputs when exactly one point is present |
| `point_values` | Inputs grouped by semantic point |
| `output_values_by_point` | Outputs grouped by semantic point |
| `report` | Underlying public `VerificationReport` |
| `task` | Compiled task retained for replay |
| `schema` | Normalized model schema retained for replay |

`input_values` and `output_values` deliberately raise `ValueError` when
flattening multiple points would be ambiguous. Use the corresponding grouped
property for pairwise or other multi-point properties.

The concrete types behind `task` and `schema` are internal. They are retained
to make the public replay operation possible, not exposed as separate V1
construction contracts.

```python
finding.point_values
# {"left": {"income": 3.0}, "right": {"income": 6.0}}
```

### Rendering and replay

```python
finding.to_text() -> str
finding.to_html() -> str
finding.replay(
    model=None,
    *,
    tolerance=1e-9,
    observer_registry=None,
) -> CounterexampleReplay
```

```python
print(finding.to_text())
html = finding.to_html()
replay = finding.replay(tolerance=1e-9)
```

Notebook display uses the same HTML representation as `to_html()`.

`replay(model=None, *, tolerance=1e-9, observer_registry=None)` uses the model
attached by artifact-based verification, or an explicitly supplied model.
`observer_registry` is an internal integration hook rather than a public V1
extension type. See [`CounterexampleReplay`](replay-and-errors.md) for replay
semantics and failure cases.
