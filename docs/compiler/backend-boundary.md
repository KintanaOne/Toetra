# Backend boundary

> **Status:** Implemented for the built-in Z3 route
>
> **Scope:** completed IR2 task through backend-neutral result

The backend boundary begins after IR2 validation. It is the first boundary
allowed to create backend-native objects.

## Implemented flow

```text
VerificationTaskIR2
→ BackendRouter
→ BackendRoute
→ BackendRunnerRegistry
→ concrete runner
→ backend-private translation
→ VerificationResult
```

There is no shared `BackendQuery` runtime class. The protocol requires a runner
to accept a routed `VerificationTaskIR2`; each adapter may create its own
private translation artifact.

## Route qualification

`BackendRouter` checks three independent dimensions:

| Dimension | Input |
|---|---|
| structural/semantic | `task.requirements` against `BackendCapabilities` |
| numeric | model, encoder, property, and backend descriptors against the compatibility registry |
| operational | `BackendExecutionPolicy` against declared execution capabilities |

An explicit backend hint must pass the same checks as automatic selection.
Failure is reported before native translation.

`BackendRoute` records:

- selected backend identity;
- capability profile;
- human-readable selection reason;
- optional numeric compatibility assessment.

## Runner resolution

The runtime uses a separate `BackendRunnerRegistry`. This separation prevents a
capability profile from being mistaken for an executor and lets tests inject a
runner without changing IR2.

The default registries contain the Z3 capability profile and `Z3Runner`.

## Z3 translation

`Z3Translator.translate(task)` produces `Z3Translation`, which contains:

- the Z3 formula for the verification condition;
- declarations/symbol identities derived from structured points;
- reverse mappings used to reconstruct backend assignments.

It recursively translates NNF, CNF, or DNF, scalar expressions, affine model
equations, internal model quantities, and supported assumptions. It rejects an
IR2 requirement or node that the adapter cannot represent.

## Execution and result

`Z3Runner` owns:

- total timeout/resource/cancellation budget;
- solver configuration;
- SAT/UNSAT/UNKNOWN interpretation under verification semantics;
- normalized assignments;
- assumption-consistency diagnostics;
- `BackendExecutionEvidence`.

It returns `VerificationResult`. Numeric and semantic-lowering conclusion
policies are applied by the high-level runtime afterward.

## Invariants

1. IR2 never imports a backend API.
2. Routing completes before translation.
3. Translation does not repair unsupported requirements.
4. Open bounds, numeric sorts, point identities, and verification semantics are
   preserved.
5. Backend-native objects do not enter public reports.
6. Technical failure is not converted into `PROVED` or `NO_WITNESS`.

## Contracts

- [IR to backend](../contracts/ir-to-backend.md)
- [Backend execution](../contracts/backend-execution-contract.md)
- [Numeric compatibility registry](../contracts/numeric-compatibility-registry.md)
- [Numeric compatibility reporting](../contracts/numeric-compatibility-reporting.md)
