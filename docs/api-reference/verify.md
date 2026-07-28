# `verify`

`verify(...)` is the public entry point for compiling and executing a Toetra
specification.

```python
--8<-- "docs/snippets/verify-session.py"
```

This block is sourced from the checked
[`verify-session.py`](../snippets/verify-session.py) example. It uses only the
public `toetra` facade.

## Signature

```python
verify(
    specification,
    *,
    model=None,
    dataset=None,
    target=None,
    schema=None,
    model_context=None,
    model_encoder_factory=None,
    ir2_context=None,
    backend_registry=None,
    numeric_compatibility_registry=None,
    runner_registry=None,
    execution_policy=None,
    anchor_source=None,
    anchor_resolver=None,
) -> VerificationSession
```

The signature above preserves every accepted keyword. The stable end-user path
uses a specification plus serialized model artifacts. Keywords whose object
types are not exported by `toetra` are described separately as advanced
injection hooks.

## Supported inputs

| Parameter | Accepted V1 use | Resolution |
|---|---|---|
| `specification` | Inline source, a `.toetra` string path, or a `Path` | A path is read as UTF-8; inline source is compiled directly |
| `model` | Serialized supported model path | Overrides the header model reference |
| `dataset` | Optional reference CSV path | Used for schema construction and, when needed, as the default anchor source |
| `target` | Optional output name | Must equal the target declared in the specification |
| `schema` | Already normalized model schema | Alternative to `model` and `dataset`; see the boundary below |
| `anchor_source` | pandas DataFrame or CSV path | Source used to resolve referenced anchors |
| `anchor_resolver` | Custom resolver object | Alternative to `anchor_source` |

When `specification` is a `.toetra` file and `model` is omitted, the
`model := ...` reference in its header is resolved relative to the
specification directory. For inline source, the header reference is resolved
from the caller's working directory. Explicit `model` and `dataset` paths are
also resolved from that working directory.

A string ending in `.toetra` is treated as a file path even when the file does
not exist. Former specification extensions are rejected.

## Input combinations

The model metadata has exactly one source:

| Inputs | Result |
|---|---|
| `model=...`, optional `dataset=...` | Toetra loads the model and builds its schema |
| neither `model` nor `schema` | Toetra loads the header model reference |
| `schema=...` only | Toetra verifies against the normalized schema |
| `schema=...` with `model` or `dataset` | `VerificationConfigurationError` |

The header target, explicit `target` and schema output must agree. Toetra
rejects a mismatch instead of allowing the property and model assumptions to
refer to different outputs.

The schema-only route is accepted by the runtime, but the schema classes are not
part of the nine-name public facade in `1.0.0rc3`. Normal application code
should therefore use model artifacts. A schema-only session also has no
concrete model attached; pass a model explicitly when replaying a finding.

## Referenced anchors

Referenced anchors require one of:

- `anchor_source=...`;
- `anchor_resolver=...`;
- a compatible `dataset=...`, reused as the default lookup source.

Providing both `anchor_source` and `anchor_resolver` is ambiguous and raises
`VerificationConfigurationError`. Inline points and properties without
referenced anchors do not require either argument.

## Return value

The function returns one
[`VerificationSession`](sessions-and-findings.md#verificationsession) after all
properties have been compiled, routed, executed and reported. The order of
session reports and findings matches the property order in the specification.

```python
from toetra import VerificationStatus, verify

session = verify("policy.toetra", model="model.joblib")

for finding in session.findings:
    if finding.status is VerificationStatus.COUNTEREXAMPLE:
        print(finding.to_text())
```

If compilation or execution raises, `verify(...)` does not return a partial
session.

## Failure boundaries

The public runtime errors are documented in
[Replay and errors](replay-and-errors.md#public-error-hierarchy).

Common call-time failures include:

| Failure | Meaning |
|---|---|
| `VerificationConfigurationError` | Inputs are ambiguous or mutually inconsistent |
| `FileNotFoundError` | A specification, model or dataset path does not exist |
| `VerificationRuntimeError` subclass | User-facing orchestration failed |
| parser, semantic, model-loading or dependency error | The corresponding stage rejected or could not load the input |

Not every compiler or third-party failure is wrapped in
`VerificationRuntimeError` in `1.0.0rc3`. Catch a narrow error when the caller
can recover from it; do not treat every exception as an inconclusive logical
status.

## Advanced injection hooks

The remaining keywords customize internal pipeline stages:

- `model_context`;
- `model_encoder_factory`;
- `ir2_context`;
- `backend_registry`;
- `numeric_compatibility_registry`;
- `runner_registry`;
- `execution_policy`.

They support Toetra development and integration testing, but their accepted
types live beneath `toetra._*`; documenting the keywords does not make those
types public. Contributor procedures for built-in integrations begin at
the [extension architecture](../development/extensions.md).
