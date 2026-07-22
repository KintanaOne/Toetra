# Results and Reports

> Status: Implemented for text, JSON and HTML/Jupyter  
> Implementation: `dsl.backends.results`, `dsl.reporting`  
> Scope: Backend-neutral verification results and user-facing report output

## Purpose

FORML separates four concerns:

```text
backend execution
→ VerificationResult
→ VerificationReport
→ text / JSON / HTML renderer
```

A backend reports what happened during execution. The reporting layer combines
that result with the FORML property, scope, route and assumptions. Renderers do
not import or inspect a concrete solver.

The internal IR pretty-printers remain developer tools. User-facing output must
consume `VerificationReport`.

## Backend-Neutral Result

`dsl.backends.results.VerificationResult` is the common execution contract:

```python
VerificationResult(
    status=VerificationStatus.COUNTEREXAMPLE,
    backend=EnumBackend.Z3,
    backend_status="sat",
    assignments={"x0.a": 3, "_model.score": 7},
    message="Property violated ...",
    diagnostics=(),
    execution=BackendExecutionEvidence(...),
)
```

The normalized statuses currently are:

| Status | Meaning |
|---|---|
| `PROVED` | No counterexample exists under the encoded assumptions |
| `COUNTEREXAMPLE` | A concrete violation was found |
| `WITNESS` | A satisfying assignment was found |
| `NO_WITNESS` | No satisfying assignment exists |
| `UNKNOWN` | The backend could not conclude |

`Z3VerificationResult` remains available as a compatibility type, but it is a
subtype of the backend-neutral result. Historical accessors `solver_status` and
`model` map to `backend_status` and `assignments`.

## Verification Report

`dsl.reporting.VerificationReport` combines:

- property index and type;
- verification semantics;
- normalized scope and variables;
- concise specification text;
- selected backend and route reason;
- backend and FORML statuses;
- normalized assignments;
- diagnostics;
- assumption count;
- numeric compatibility route, semantic target and conclusion scope;
- backend execution status, duration, reason and policy snapshot;
- content-addressed verification provenance and completeness.
- per-evaluation output-observable evidence and semantic-lowering traces.

Assignments are classified as:

```text
INPUT      x0.a
OUTPUT     _model.score → score
AUXILIARY  internal model quantities and backend-introduced names
```

Classification labels and probabilities are not forced into the legacy scalar
`OUTPUT` collection. They are exposed through `report.model_evaluations`, which
retains the public intent, reconstructed views, native decision policy, internal
quantity and lowering evidence. Reconstructed probabilities are marked as
approximate presentation evidence; proof soundness continues to rely on the
canonical constraint and numeric compatibility policy.

This distinction lets all renderers display a counterexample without exposing
backend naming conventions. Application code can also access normalized values:

```python
assignment.exact_value   # Fraction(1, 3)
assignment.python_value  # 0.3333333333333333
report.input_values      # {"a": 3.0}
report.output_values     # {"score": 7.0}
```

The original backend object remains available as `assignment.value` for advanced
diagnostics only.

## Numeric compatibility evidence

Compatibility-aware reports expose the matched framework/model/encoder/backend rule rather than asking renderers to infer meaning from a concrete solver.

```python
report.numeric_compatibility.classification
report.numeric_compatibility.semantic_target
report.numeric_compatibility.conclusion_scope
report.numeric_compatibility.source_route
report.numeric_compatibility.backend_route
```

When the conclusion applies only to an encoded abstraction, the report summary, text renderer, JSON payload and HTML card all state that boundary. A `PROVED` result therefore cannot silently appear to certify bit-exact source execution.

The complete contract is documented in [Numeric Compatibility Reporting](../contracts/numeric-compatibility-reporting.md).


## Backend execution evidence

The logical FORML status and the technical backend status are separate:

```python
report.status                       # VerificationStatus.UNKNOWN
report.backend_execution.status     # "timeout"
report.backend_execution.duration_ms
report.backend_execution.timeout_ms
report.backend_execution.backend_reason
```

Timeout, resource exhaustion and cancellation therefore remain visible in text, JSON, HTML and session records. Technical adapter failures raise `BackendExecutionError` instead of producing a misleading logical `UNKNOWN`. The complete contract is documented in [Backend Execution Contract](../contracts/backend-execution-contract.md).

## Verification provenance

Every completed report identifies the verification configuration without relying on mutable filenames:

```python
report.provenance.input_fingerprint
report.provenance.property_fingerprint
report.provenance.route_fingerprint
report.provenance.execution_policy_fingerprint
report.provenance.verification_fingerprint
report.provenance.completeness
```

Files use raw-byte fingerprints. Inline specifications, schemas and pandas anchors use explicit versioned canonicalization. Opaque resolvers produce `partial` provenance rather than fabricated evidence. Collections carry only evidence shared by all properties. SHA-256 provides content identity, not signatures or chain-of-custody guarantees. See the [Verification Provenance Contract](../contracts/verification-provenance.md).

## Text Rendering

The default renderer is available as a method:

```python
print(report.to_text())
```

or as a standalone function:

```python
from dsl.reporting import render_verification_reports_text

print(render_verification_reports_text(reports))
```

The renderer displays:

- the normalized FORML status;
- the property and scope;
- the concise specification;
- backend and routing information;
- the conclusion;
- grouped input, output and auxiliary assignments;
- structured diagnostics.

ASCII-only output is supported for restricted terminals:

```python
from dsl.reporting import TextRenderOptions

print(
    report.to_text()
    if supports_unicode
    else render_verification_report_text(
        report,
        options=TextRenderOptions(use_unicode=False),
    )
)
```

## Stable JSON Contract

Every JSON payload is explicitly versioned:

```json
{
  "schema": "forml.verification-report",
  "schema_version": 5
}
```

One report can be serialized or written directly:

```python
payload = report.to_dict()
json_text = report.to_json()
report.write_json("artifacts/property-1.json")
```

A report collection uses a separate envelope:

```python
from dsl.reporting import write_verification_reports_json

write_verification_reports_json(reports, "artifacts/forml-report.json")
```

Its schema identifier is:

```text
forml.verification-report-collection
```

Z3 integer values become JSON integers. Exact non-integral rationals preserve
their numerator and denominator rather than being rounded:

```json
{
  "kind": "rational",
  "numerator": 1,
  "denominator": 3,
  "text": "1/3"
}
```

Historical schemas remain as golden fixtures. Schema version 3 added `numeric_compatibility`. Schema version 4 added backend execution evidence. Schema version 5 adds content-addressed artifact, software, compiler, route and verification provenance; it is protected by `verification_report_v5.json`. P21.9 extends v5 additively with an optional `model_evaluations` field; no existing assignment or provenance field changes meaning.

## HTML and Jupyter Rendering

A report or complete session can be returned directly from a notebook cell:

```python
report
session
```

Both objects expose `_repr_html_()` through their public `to_html()` method.
The renderer is backend-neutral, escapes all specification, diagnostic and
assignment text, and uses no JavaScript or external assets.

Standalone review artifacts are available through:

```python
report.write_html("property.html")
session.write_html("verification-session.html")
```

The generated document includes inline CSS, a status summary, one card per
property, grouped inputs and model outputs, route information and diagnostics.
It can therefore be attached to a model-review ticket without a running FORML
or Jupyter environment.

## Current Boundary

Implemented:

```text
Z3 native status
→ VerificationResult
→ VerificationReport
→ shared text renderer
→ stable JSON export
→ HTML/Jupyter representation
```

High-level runtime integration:

```text
forml.verify(...)
→ VerificationSession
→ filtered findings and reports
→ text / JSON / HTML / data-frame helpers
→ optional estimator replay
```

The user-facing presentation layer is complete for terminal, automation and
notebook workflows. Future presentation work may add richer domain/model
explanations, interactive exploration or a web application, but those are not
required by the current V1 profile.

## Point-Aware Evidence

Patch 15.11 adds grouped evidence without removing the historical one-point conveniences.

```python
report.point_values
# {"x0": {"a": 1.0}, "x1": {"a": 2.0}}

report.point_output_values
# {"x0": {"score": 3.0}, "x1": {"score": 5.0}}
```

Each `ReportPointEvidence` retains its binding kind, source values, solver values, provenance and indexed outputs. `input_values` and `output_values` remain available only when one point is unambiguous; multi-point flattening raises explicitly.

JSON emits a structured `points` array for multi-point evidence and anchored evidence. Text and HTML render one point group at a time. Session records keep their stable columns while storing nested point maps in `inputs` and `outputs` for multi-point properties.

## Multi-Point Replay

Replay is performed once for every distinct point referenced by a model output:

```python
replay = finding.replay()
replay.inputs_by_point
replay.outputs_by_point
replay.relation_consistent
replay.assertion_consistent
```

A replay is consistent only when every formal/concrete output comparison is within tolerance and every supported concrete relation/assertion check agrees with the formal result. Missing model features produce a `REPLAY_POINT_MISSING` failure; FORML never reports a silently partial replay.
