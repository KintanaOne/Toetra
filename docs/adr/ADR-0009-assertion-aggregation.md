# ADR-0009 — Introduce Assertion Aggregation Before Backend Lowering

> Status: Accepted and implemented
> Date: 2026-06  
> Scope: Logical verification pipeline

## Context

Toetra verification is not only the direct translation of user assertions.

A complete verification problem may include:

- DSL assertions,
- scope constraints,
- domain constraints,
- neighborhood constraints,
- semantic constraints,
- model-derived constraints,
- backend capability constraints.

These pieces must be combined before backend lowering.

## Decision

Toetra introduces an Assertion Aggregation layer.

The output of this layer is an `AggregatedAssertionSet`.

## Rationale

Aggregation separates logical composition from backend encoding.

It also makes it possible to inspect, minimize, mutate, and test the verification problem before sending it to a solver.

## Consequences

### Positive

- Backend lowering receives a complete verification problem.
- ModelBridge constraints can be integrated cleanly.
- Redundant or conflicting constraints can be detected earlier.
- Miova can mutate aggregated assertions as a dedicated artifact kind.

### Negative

- Aggregation requires traceability to source assertions.
- Constraint provenance must be preserved.
- Incorrect aggregation can change verification semantics.

## Alternatives considered

### Lower each assertion independently

Rejected because verification may require global composition.

### Let Z3-specific lowering perform aggregation

Rejected because aggregation should remain backend-independent.

## Impact on Toetra

Assertion aggregation is a critical planned P0 layer for end-to-end verification.
