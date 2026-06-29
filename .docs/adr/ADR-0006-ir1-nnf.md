# ADR-0006 — Define IR1 as NNF-Oriented Logical Representation

> Status: Accepted  
> Date: 2026-06  
> Scope: Intermediate representations

## Context

After semantic validation, FORML needs a backend-independent representation of the verification query.

This representation should be independent from DSL syntax, but not yet optimized for a specific backend.

It should also simplify logical reasoning by normalizing negations and implications.

## Decision

IR1 is defined as the first backend-independent logical representation.

IR1 is responsible for:

- preserving semantic scope,
- representing verification tasks,
- representing logical expressions,
- preserving problem-level predicates,
- eliminating or preparing implication handling,
- applying De Morgan transformations,
- moving logic toward Negation Normal Form.

## Rationale

NNF is a useful early normal form because it pushes negations toward atomic predicates while preserving a readable logical structure.

It prepares later transformations without forcing an early CNF/DNF choice.

## Consequences

### Positive

- IR1 remains backend-independent.
- IR1 is easier to inspect than backend-specific encodings.
- IR2 can later choose CNF or DNF depending on verification needs.
- De Morgan / NNF transformations can be tested independently.

### Negative

- IR1 is not always directly solver-ready.
- A second IR layer is needed for clause-oriented forms.
- The exact NNF invariant must be tested carefully.

## Alternatives considered

### Produce CNF directly from SemanticValidatedAST

Rejected because CNF is not always the desired next form and can cause structural blow-up.

### Send raw logical AST to backend lowering

Rejected because backend lowering should receive normalized logic, not user syntax.

## Impact on FORML

IR1 is the logical stabilization layer.

It should be covered by golden tests, property-based tests, and Miova mutation campaigns.
