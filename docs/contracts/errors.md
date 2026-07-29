# Error Boundaries Contract

> Status: Accepted internal and public taxonomy
>
> Scope: Failure ownership across the language and verification pipeline
>
> Audience: maintainers, diagnostic authors, testers and Miova campaign authors

## Purpose

A failure is useful only when Toetra reports the correct owning boundary and preserves the original cause.

---

## Public boundary

The internal layer that owns a failure and the public class that presents it
are separate decisions.

| Failure class | Public presentation from `verify(...)` |
|---|---|
| invalid syntax, AST structure, semantic input, artifact, or configuration | `VerificationConfigurationError` |
| valid but unsupported model, compatibility, or backend route | `VerificationRuntimeError` |
| technical routing, translation, runner, or backend failure | `VerificationRuntimeError` |
| incomplete concrete replay | `ReplayUnavailableError` |
| logical verification outcome | session/report status, never an exception |

Public normalization must retain the owning layer in `stage` and the original
exception in `__cause__`. It must not turn a private class into a public
compatibility promise.

The complete decision is recorded in
[ADR-0029](../adr/ADR-0029-public-verification-failure-boundary.md).

---

## Boundary Families

| Boundary | Error family | New feature examples |
|---|---|---|
| Source → CST | Parser/Syntax | missing quantified identifier, malformed interval |
| CST → AST | Builder/Structure | missing scalar operand, unrepresentable domain entry |
| AST → Semantic | Binding/Type/Domain | `forall x0` with `y.a`, invalid arithmetic types |
| Semantic → IR1 | IR lowering contract | lost resolved symbol, lost quantifier kind |
| IR1 → IR2 | Normalization/Assumption | invalid DOMAIN assumption provenance |
| Aggregation | Composition | existential property negated as universal |
| Routing | Compatibility | no backend supports symbolic division |
| Backend compilation | Encoding | unsupported sort or categorical encoding |
| Runtime | Solver execution/result | solver failure or semantics-inconsistent result |

---

## Required public diagnostic fields

Every public verification error exposes:

- `message`;
- stable `code`;
- stable owning `stage`;
- optional `hint`;
- optional `path`;
- optional one-based `line` and `column`.

Callers branch on `code`, not prose. Unavailable context is `None`.

Internal structured diagnostics should additionally expose when available:

- property identity;
- source span;
- offending identifier/operator/domain entry;
- expected declaration/type/capability;
- actual declaration/type/capability;
- causal exception;
- provenance chain;
- expected-vs-unexpected classification for mutation campaigns.

---

## Implemented compiler normalization

P26.1 implements the public boundary for the first three compiler transitions:

| Internal owner | Public class from `verify(...)` | `stage` | Stable codes |
|---|---|---|---|
| source → CST | `VerificationConfigurationError` | `syntax` | `PARSER_INVALID_SYNTAX`, `PARSER_UNEXPECTED_CHARACTER`, `PARSER_UNEXPECTED_TOKEN`, `PARSER_UNEXPECTED_END_OF_INPUT` |
| CST → AST | `VerificationConfigurationError` | `builder` | `BUILDER_INVALID_STRUCTURE` plus compatible specific builder codes |
| AST → semantic state | `VerificationConfigurationError` | `semantic` | `SEMANTIC_INVALID`, `SEMANTIC_INVALID_PROPERTY`, `SEMANTIC_UNBOUND_VARIABLE`, `SEMANTIC_TYPE_MISMATCH`, `SEMANTIC_INVALID_OPERATOR`, `SEMANTIC_INCOMPATIBLE_FUNCTION`, `SEMANTIC_INVALID_ARITHMETIC`, `SEMANTIC_INVALID_DOMAIN`, `SEMANTIC_INVALID_OUTPUT_OBSERVABLE` |

The parser converts Lark failures at its own boundary. Semantic validators
propagate `SemanticError` and its subclasses; they never relabel them as
`ParserError`. Unexpected implementation exceptions remain internal failures
instead of being presented as invalid user input.

Source location is one-based. Syntax failures use the parser location.
Semantic failures use the nearest reliable AST `SourceSpan`; Toetra leaves the
location unset rather than inventing a narrower span.

---

## Implemented artifact and model normalization

P26.2 normalizes specification artifacts and the model-loading bridge:

| Internal owner | Public class from `verify(...)` | `stage` | Stable codes |
|---|---|---|---|
| specification file | `VerificationConfigurationError` | `configuration` | `SPECIFICATION_NOT_FOUND`, `SPECIFICATION_ENCODING_INVALID`, `SPECIFICATION_READ_FAILED` |
| model and dataset artifacts | `VerificationConfigurationError` | `model` | `MODEL_ARTIFACT_NOT_FOUND`, `MODEL_ARTIFACT_FORMAT_UNSUPPORTED`, `MODEL_ARTIFACT_DESERIALIZATION_FAILED`, `MODEL_ARTIFACT_INVALID`, `MODEL_DATASET_NOT_FOUND`, `MODEL_DATASET_READ_FAILED`, `MODEL_FEATURE_METADATA_REQUIRED` |
| loaded but unsupported model integration | `VerificationRuntimeError` | `model` | `MODEL_TYPE_UNSUPPORTED`, `MODEL_FRAMEWORK_UNSUPPORTED` |
| model detection or introspection failure | `VerificationRuntimeError` | `model` | `MODEL_DETECTION_FAILED`, `MODEL_INTROSPECTION_FAILED`, `MODEL_PROCESSING_FAILED` |

An absent, unreadable, or incoherent artifact is invalid input. A model that
loads correctly but has no complete Toetra integration is instead a valid but
unsupported route. Both retain the original private cause when one exists.

P26.2 intentionally left encoder, model-semantic, compatibility, routing, and
backend failures to later P26 steps.

---

## Implemented supported-route normalization

P26.3 normalizes valid but unsupported model and backend routes without
changing the built-in V1 profile:

| Internal owner | Public class from `verify(...)` | `stage` | Stable codes |
|---|---|---|---|
| model encoder | `VerificationConfigurationError` only for missing required schema parameters; otherwise `VerificationRuntimeError` | `model` | `MODEL_ENCODER_UNSUPPORTED`, `MODEL_ENCODER_PARAMETER_MISSING`, `MODEL_ENCODER_PARAMETER_UNSUPPORTED`, `MODEL_ENCODER_OUTPUT_INVALID`, `MODEL_ENCODING_FAILED` |
| model semantic lowering | `VerificationRuntimeError` | `model` | `MODEL_SEMANTIC_PROFILE_UNSUPPORTED`, `MODEL_OBSERVABLE_UNSUPPORTED`, `MODEL_SEMANTIC_PROFILE_INVALID`, `MODEL_SEMANTIC_LOWERING_INCOMPLETE`, `MODEL_SEMANTIC_LOWERING_FAILED` |
| numeric compatibility | `VerificationRuntimeError` | `compatibility` | `NUMERIC_COMPATIBILITY_ROUTE_UNSUPPORTED`, `NUMERIC_COMPATIBILITY_AMBIGUOUS`, `NUMERIC_COMPATIBILITY_INVALID` |
| backend selection | `VerificationRuntimeError` | `routing` | `BACKEND_NOT_REGISTERED`, `BACKEND_ROUTE_UNSUPPORTED`, `BACKEND_ROUTING_FAILED` |

The router distinguishes structural capability rejection from numeric
compatibility rejection before the public boundary. An empty or non-executable
numeric route therefore does not masquerade as a generic backend-capability
failure.

Unexpected exceptions outside these owned families remain implementation
failures and are not relabeled as user input.

---

## Implemented backend execution normalization

P26.4 completes the public backend boundary without changing logical result
semantics:

| Internal owner | Public class from `verify(...)` | `stage` | Stable codes |
|---|---|---|---|
| runner registry | `VerificationRuntimeError` | `backend` | `BACKEND_RUNNER_NOT_REGISTERED` |
| backend translation | `VerificationRuntimeError` | `backend` | `BACKEND_TRANSLATION_REQUIREMENTS_UNSUPPORTED`, `BACKEND_SCALAR_EXPRESSION_UNSUPPORTED`, `BACKEND_SYMBOL_COLLISION`, `BACKEND_TRANSLATION_FAILED` |
| backend execution policy | `VerificationConfigurationError` | `backend` | `BACKEND_EXECUTION_POLICY_INVALID` |
| technical backend execution | `VerificationRuntimeError` | `backend` | `BACKEND_EXECUTION_FAILED` |

The backend adapter raises its own structured private errors. `verify(...)`
translates only those owned families and preserves them through `__cause__`.
An arbitrary exception from a custom runner remains an implementation failure
instead of being mislabeled.

Timeout, resource exhaustion, cancellation, and solver `unknown` remain
inconclusive logical results with separate `BackendExecutionEvidence`. A
technical adapter exception remains an exception and never becomes `UNKNOWN`.

---

## Recommended Diagnostic Codes

Exact exception class names remain implementation choices, but stable diagnostics should cover:

```text
PARSER_MISSING_QUANTIFIED_IDENTIFIER
PARSER_INVALID_INTERVAL_DELIMITERS
BUILDER_MALFORMED_SCALAR_EXPRESSION
BUILDER_MALFORMED_DOMAIN_ENTRY
SEMANTIC_UNBOUND_EXPLICIT_ENTITY
SEMANTIC_QUANTIFIED_ENTITY_MISMATCH
SEMANTIC_IMPLICIT_DOMAIN_SUBJECT
SEMANTIC_DUPLICATE_DOMAIN_SUBJECT
SEMANTIC_TARGET_IN_INPUT_DOMAIN
SEMANTIC_EMPTY_INTERVAL
SEMANTIC_INCOMPATIBLE_SET_MEMBER
SEMANTIC_NON_NUMERIC_ARITHMETIC
SEMANTIC_LITERAL_DIVISION_BY_ZERO
IR1_MISSING_RESOLVED_REFERENCE
IR1_LOST_QUANTIFIER_KIND
IR2_INVALID_DOMAIN_ASSUMPTION
AGGREGATION_INVALID_VERIFICATION_SEMANTICS
BACKEND_UNSUPPORTED_AFFINE_ARITHMETIC
BACKEND_UNSUPPORTED_NONLINEAR_ARITHMETIC
BACKEND_UNSUPPORTED_SYMBOLIC_DIVISION
BACKEND_UNSUPPORTED_SCALAR_SORT
BACKEND_UNSUPPORTED_CATEGORY_ENCODING
```

---

## Binding Diagnostic Example

For:

```toetra
forall x0 => y.a <= 3
```

Toetra should report conceptually:

```text
Explicit entity `y` is not declared by quantified scope `forall x0`.
Expected entity: x0.
Implicit feature syntax `a` may be used when the default entity is intended.
```

It must not silently reinterpret `y.a` as `x0.a`.

---

## Capability Diagnostic Example

For a meaningful but unsupported expression:

```toetra
forall x0 => x0.a * x0.b <= target
```

the diagnostic belongs to requirement/routing/backend compatibility, not parsing or semantic typing:

```text
The property requires nonlinear multiplication.
Requested backend Z3 profile declares affine arithmetic only.
```

---

## Expected Failure Semantics

| Classification | Meaning |
|---|---|
| Expected rejection | Invalid artifact rejected at its owning boundary. |
| Wrong-boundary rejection | Invalid artifact rejected, but contract ownership is violated. |
| False rejection | Valid artifact rejected. |
| False acceptance | Invalid artifact reaches a later layer. |
| Internal failure | Unclassified exception, assertion crash or corrupted state. |

Miova campaigns should distinguish all five.

## Specification Constant Diagnostics

The semantic/type boundary owns diagnostics for:

- duplicate specification-constant declarations;
- reserved declaration names;
- collisions with scope variables;
- unresolved bare names;
- incompatible constant uses;
- unsupported declaration literal kinds.

A parser error is appropriate only when declaration syntax is malformed. A backend-capability diagnostic is appropriate when the constant is semantically valid but its type cannot be encoded by the selected backend profile.
