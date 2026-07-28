# Backend routing and orchestration

> **Status:** Implemented routing; Z3 is the only built-in V1 backend
>
> **Scope:** backend qualification and runner selection

Backend routing answers:

> Which registered backend can execute this completed IR2 task under the
> requested numeric and operational contracts?

## Inputs and output

```text
VerificationTaskIR2
+ backend registry
+ numeric compatibility context
+ execution policy
→ BackendRoute
```

`BackendRoute` contains the selected backend, its capabilities, a route reason,
and the numeric compatibility assessment.

## Explicit selection

A source-level `using Z3` hint constrains the router to Z3. The requested backend
must still:

- be registered;
- satisfy every `IR2Requirement`;
- have an executable numeric compatibility rule;
- enforce the requested execution controls.

An incompatible explicit backend is rejected. It is never silently replaced.

## Automatic selection

Without a hint, `BackendRouter` iterates registered capability profiles and
returns the first route satisfying all checks. The default V1 registry contains
only Z3, so this is deterministic backend qualification rather than
multi-backend optimization.

## Three qualification gates

### Structural and semantic capabilities

`BackendCapabilities.incompatibilities(...)` checks logical forms, arithmetic,
sorts, assumptions, quantifier semantics, point-aware evaluations, and
model-semantic quantities.

### Numeric compatibility

The compatibility registry evaluates the source framework, model encoder,
property requirements, backend numeric profile, and non-finite-value policy. A
route can be structurally expressible but numerically non-executable.

### Execution policy

Execution capabilities are compared with timeout, cancellation, resource,
deterministic-seed, and backend-option requirements. Unsupported controls fail
closed.

## Runner selection

Capabilities and executors live in separate registries:

```text
BackendRegistry
→ route qualification

BackendRunnerRegistry
→ concrete execution after routing
```

The runtime requires a runner for the selected backend and passes it the same
IR2 task plus execution policy.

## Not part of V1 orchestration

- performance-based backend ranking;
- concurrent multi-backend execution;
- voting or result comparison;
- fallback after a backend times out;
- automatic abstraction-strategy search;
- remote/distributed scheduling;
- AutoToetra decisions.

These are post-V1 directions and must not be inferred from the existence of the
router.

## Contracts

- [IR to backend](../contracts/ir-to-backend.md)
- [Numeric compatibility registry](../contracts/numeric-compatibility-registry.md)
- [Backend execution](../contracts/backend-execution-contract.md)
