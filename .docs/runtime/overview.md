# Runtime Overview

> Status: Planned  
> Implementation: Not yet implemented  
> Scope: Target runtime architecture after backend query generation

## Purpose

The FORML runtime is the target execution layer responsible for running a prepared verification query against a verification backend and returning structured results.

The runtime is not part of the language frontend. It starts after the compiler, ModelBridge, IR normalization, assertion aggregation, and lowering stages have produced a backend-ready artifact.

FORML should not execute raw DSL properties directly.

Instead, the target runtime path is:

```text
.forml source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1-NNF
→ IR2-CNF/DNF
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
→ Verification Runtime
→ VerificationResult
```

## Current V1 Runtime Scope

FORML V1 should target a minimal but functional runtime based on Z3.

```text
BackendQuery
→ Z3 runtime adapter
→ Z3 solver execution
→ VerificationResult
```

Z3 is the minimal backend for the first complete end-to-end version.

Other backends such as ERAN, zonotope-based analyzers, abstract interpretation engines, or neural network verifiers are future extensions and should be considered post-V1.

## Runtime Responsibilities

The runtime is responsible for:

- receiving a backend-specific query artifact,
- executing the corresponding backend adapter,
- collecting solver or verifier results,
- normalizing backend-specific outputs,
- exposing structured diagnostics,
- preserving traceability back to FORML artifacts.

## Runtime Non-Responsibilities

The runtime must not:

- parse FORML source code,
- build AST nodes,
- perform semantic binding,
- decide CNF/DNF transformations,
- perform assertion aggregation,
- mutate artifacts,
- infer model metadata.

Those responsibilities belong to earlier layers.

## Main Runtime Artifacts

| Artifact | Role |
|---|---|
| `BackendQuery` | Backend-specific executable representation |
| `RuntimeExecutionContext` | Runtime metadata, options, limits, and execution settings |
| `VerificationResult` | Normalized result returned by the backend |
| `DiagnosticTrace` | Traceability and debugging information |
| `BackendError` | Structured failure returned when execution cannot complete |

## Minimal V1 Runtime Contract

The minimal runtime contract should support:

```text
Input:
    BackendQuery

Output:
    VerificationResult

Required backend:
    Z3

Guarantees:
    - Backend-specific execution errors are normalized.
    - Solver status is exposed.
    - Counterexamples are preserved when available.
    - The result can be traced back to the original FORML property.
```

## Relationship With Backends

The runtime is backend-facing but should remain isolated from backend implementation details.

Each backend should expose an adapter boundary:

```text
BackendQuery
→ BackendAdapter
→ Native backend call
→ BackendRawResult
→ VerificationResult
```

For V1, the only required adapter is the Z3 adapter.

## Relationship With Miova

Miova is not part of the normal runtime execution path.

Miova may be used to challenge runtime inputs and outputs, for example:

- mutate `BackendQuery`,
- mutate runtime options,
- validate expected runtime failures,
- test diagnostic consistency,
- explore solver boundary cases.

The normal verification path remains deterministic and non-mutating.

## Runtime Maturity Levels

| Level | Description | Status |
|---|---|---|
| R0 | BackendQuery artifact defined | Planned |
| R1 | Z3 adapter executes simple queries | Planned |
| R2 | VerificationResult normalized | Planned |
| R3 | Counterexamples and diagnostics exposed | Planned |
| R4 | Runtime options and limits supported | Planned |
| R5 | Monitoring and observation hooks | Future |
| R6 | Multi-backend runtime orchestration | Post-V1 |

## Design Principle

The runtime should be small at first.

FORML V1 should prefer:

```text
one backend
one execution path
one normalized result model
clear diagnostics
```

over premature multi-backend orchestration.

The goal of V1 is not backend breadth. The goal is a complete, reliable, end-to-end verification path.
