# ADR-0002 — Treat Each Compiler Layer as a Distinct Artifact

> Status: Accepted  
> Date: 2026-06  
> Scope: Artifact model

## Context

Toetra manipulates different representations of the same user intent:

- source text,
- CST,
- AST,
- semantic AST,
- IR1,
- IR2,
- aggregated assertions,
- lowered queries,
- backend queries.

These representations are related, but they are not interchangeable.

## Decision

Each compiler layer is treated as a distinct artifact with its own identity, invariants, and contract.

Example artifact kinds:

```text
toetra.source
toetra.cst
toetra.ast
toetra.semantic_ast
toetra.ir1
toetra.ir2
toetra.model_schema
toetra.model_constraints
toetra.aggregated_assertions
toetra.lowered_query
toetra.backend_query
```

## Rationale

Layered artifacts make it possible to define clear boundaries.

They also make Toetra compatible with Miova's mutation model, where each artifact kind can be mutated, validated, accepted, rejected, or classified as an expected failure.

## Consequences

### Positive

- Each representation has a clear responsibility.
- Tests can target precise layers.
- Mutations can be scoped to a layer.
- Debugging becomes easier.
- Documentation can describe exact contracts.

### Negative

- More types and artifacts must be maintained.
- Cross-layer traceability must be designed carefully.
- Developers must avoid leaking implementation details across layers.

## Alternatives considered

### Single mutable object passed through the whole pipeline

Rejected because it makes validation, mutation, diagnostics, and traceability harder.

### Pure backend-oriented representation from the start

Rejected because backend-specific concerns should not pollute early compiler layers.

## Impact on Toetra

The artifact model is foundational for compiler contracts, testing strategy, and Miova integration.
