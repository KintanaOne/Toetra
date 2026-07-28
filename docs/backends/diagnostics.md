# Backend diagnostics

> **Status:** Implemented across routing, execution evidence, IR2 diagnostics,
> and public reports

Toetra separates invalid input, unsupported routes, technical termination, and
logical conclusions. There is no single public `BackendDiagnostic` class.
Evidence is carried by the owning boundary.

## Diagnostic ownership

| Situation | Owning representation |
|---|---|
| backend not registered | structured backend error |
| capability mismatch | routing error with incompatibility reasons |
| numeric route unavailable | routing error with compatibility diagnostics |
| execution control unsupported | routing error with policy incompatibilities |
| IR2 structural warning | `IR2Diagnostic` on the task |
| timeout/resource/cancellation/unknown | `BackendExecutionEvidence` |
| backend technical exception | `BackendExecutionError` with execution evidence |
| proof/counterexample/witness/no witness | `VerificationResult`, then `VerificationReport` |
| conclusion weakened by compatibility | final report status and compatibility evidence |

## Invalid, unsupported, inconclusive, and violated

| Class | Meaning | Runtime behavior |
|---|---|---|
| invalid | source, binding, type, model, or configuration contract is broken | exception before backend execution |
| unsupported | valid request has no compatible model/encoder/backend route | fail-closed exception |
| inconclusive | compatible backend ran but did not justify a conclusion | report status `UNKNOWN` |
| violated | universal-refutation query is satisfiable | `COUNTEREXAMPLE` report |
| verified | universal-refutation query is unsatisfiable | `PROVED` report |

Existential semantics similarly distinguish `WITNESS` and `NO_WITNESS`.

## Route explanations

Successful reports retain `route_reason`. It identifies whether the backend was
explicitly requested or automatically qualified and summarizes the numeric
compatibility route.

Failed routing messages enumerate the rejected capability or policy dimensions.
They do not insert artificial logical assumptions or try another backend after
an explicit choice.

## Technical termination evidence

`BackendExecutionEvidence` records:

- normalized execution status;
- total duration;
- immutable policy snapshot;
- user-readable reason;
- optional native backend reason.

Technical status remains separate from logical status. For example, a timeout is
reported as logical `UNKNOWN` plus technical `TIMEOUT`, not as a failed proof.

## IR2 diagnostics

IR2 guardrails can record structural diagnostics about model-evaluation
equations and assumptions. These are attached before routing and rendered with
the verification report when execution remains valid.

Missing or contradictory information that would make execution unsound is an
error rather than a warning.

## Public handling

The public API exposes stable report/status types and documented exception
families. Private backend and compiler exception subclasses may change without
becoming public imports.

P26 owns improvements to wording, codes, and user guidance. Such changes must
preserve the boundary distinctions documented here.

## Contracts

- [Error boundaries](../contracts/errors.md)
- [IR to backend](../contracts/ir-to-backend.md)
- [Backend execution](../contracts/backend-execution-contract.md)
- [Numeric compatibility reporting](../contracts/numeric-compatibility-reporting.md)
- [Public API errors](../api-reference/replay-and-errors.md)
