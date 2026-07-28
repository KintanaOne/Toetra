# ADR-0029 — Normalize Public Verification Failures Without Erasing Ownership

> Status: Accepted
> Date: 2026-07
> Scope: `toetra.verify(...)`, replay, and user-facing diagnostics

## Context

The staged compiler and runtime already use precise private exception families
for parsing, semantic validation, model handling, IR construction, routing, and
backend execution. Those boundaries are valuable for maintenance, testing, and
Miova failure classification.

The public `verify(...)` workflow nevertheless exposes some of those private
classes directly. Callers cannot handle failures uniformly without importing
`toetra._*`, and prose-only messages do not provide a stable machine-readable
identity.

The nine-symbol public facade already exports the required public families:

- `VerificationConfigurationError`;
- `VerificationRuntimeError`;
- `ReplayUnavailableError`.

P26 must improve this boundary without adding exports, changing proof
semantics, or treating a logical result as an exception.

## Decision

### Public classification

The normal public workflow uses the following classification:

| Situation | Public behavior |
|---|---|
| invalid specification, semantic input, artifact, or call configuration | `VerificationConfigurationError` |
| valid request with no supported execution route | `VerificationRuntimeError` |
| technical routing, translation, or backend failure | `VerificationRuntimeError` |
| formal evidence cannot be replayed completely | `ReplayUnavailableError` |
| proved, refuted, witnessed, not witnessed, or inconclusive property | `VerificationSession` and reports |

`ReplayUnavailableError` remains a specialized
`VerificationRuntimeError`. Private subclasses may refine configuration or
runtime failures but are not public compatibility promises.

### Structured diagnostic contract

Every public verification error exposes:

| Attribute | Contract |
|---|---|
| `message` | human-readable summary; equivalent to `str(error)` |
| `code` | stable uppercase identifier for programmatic handling |
| `stage` | stable owning-stage identifier |
| `hint` | optional remediation guidance |
| `path` | optional user-facing source or artifact path |
| `line`, `column` | optional one-based source location |

The stable stage vocabulary is:

```text
configuration
syntax
builder
semantic
model
anchor
compatibility
routing
backend
runtime
replay
```

Fields that are not available are `None`; Toetra does not invent source
locations or remediation advice.

### Cause preservation

Normalization uses explicit exception chaining:

```python
raise public_error from private_error
```

The private cause therefore remains inspectable through `__cause__` for
debugging without making its class a public import.

### Code stability

Callers may branch on `code`, not on message text. Message wording and private
exception classes may improve in compatible releases. Existing code meanings
must not be reused for a different failure. New codes may be added
compatibly.

## Rationale

This design gives normal users one coherent handling surface while preserving
the internal layer boundaries accepted by ADR-0011. It also supports tests and
Miova campaigns that need to distinguish syntax, semantics, support, technical
execution, and logical outcomes.

Keeping stage and code as strings avoids adding a public enum to the frozen
nine-symbol facade.

## Consequences

### Positive

- callers no longer need private imports for normal failure handling;
- diagnostics are actionable without parsing prose;
- original exceptions remain available for debugging;
- syntax and semantic ownership remain distinct;
- the public facade remains unchanged.

### Negative

- the `verify(...)` boundary requires explicit translation tables;
- each new failure path must choose a stable code and correct owner;
- source positions and hints are optional until their owning layer provides
  reliable evidence.

## Alternatives considered

### Expose every internal exception publicly

Rejected because it would freeze implementation details across the compiler,
model bridge, and backend layers.

### Wrap every failure in one generic exception

Rejected because callers and mutation campaigns could no longer distinguish
invalid input, unsupported capability, technical failure, and replay failure.

### Encode the category only in message text

Rejected because prose is not a stable programmatic interface.

### Convert backend failure to logical `UNKNOWN`

Rejected because technical execution evidence cannot justify a logical
conclusion.

## Impact on Toetra

P26 implements the decision incrementally:

1. establish the structured public error contract;
2. preserve syntax and semantic ownership while normalizing compiler failures;
3. normalize model, artifact, compatibility, routing, and backend failures;
4. test the public error matrix end to end.

No step changes the language, the supported model routes, backend support,
verification semantics, report schema, or public export count.
