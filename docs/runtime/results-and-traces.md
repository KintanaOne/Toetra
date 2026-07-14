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
- assumption count.

Assignments are classified as:

```text
INPUT      x0.a
OUTPUT     _model.score → score
AUXILIARY  backend-introduced names
```

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
  "schema_version": 1
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

The version-1 contract is protected by a golden fixture under
`test/fixtures/reporting/golden/`.

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
