# ADR-0007 — Define IR2 as CNF/DNF Normal-Form Layer

> Status: Planned  
> Date: 2026-06  
> Scope: Intermediate representations

## Context

IR1 provides a normalized backend-independent logical representation, especially around De Morgan and NNF.

However, different verification strategies may require different logical shapes.

For example:

- SAT/SMT-style solving often benefits from CNF-like structures,
- scenario exploration and case-splitting may benefit from DNF-like structures,
- minimization may require canonicalized assertion sets.

## Decision

Toetra will introduce IR2 as the normal-form selection layer.

IR2 is responsible for producing clause-oriented or case-oriented representations such as:

```text
CNF
DNF
future canonical forms
```

depending on verification needs.

## Rationale

IR2 prevents IR1 from becoming overloaded.

IR1 answers:

```text
What is the normalized logical structure?
```

IR2 answers:

```text
Which logical form is best suited for the next verification step?
```

## Consequences

### Positive

- CNF/DNF selection is explicit.
- IR1 remains readable and general.
- Backend preparation becomes cleaner.
- Logical rewrites can be tested as standalone contracts.

### Negative

- IR2 may increase implementation complexity.
- Some transformations may preserve equisatisfiability rather than strict equivalence.
- Traceability from IR2 back to user assertions must be preserved.

## Alternatives considered

### Use only IR1

Rejected because backend preparation and normal-form selection would pollute IR1.

### Create backend-specific IR2 per backend

Rejected for V1 because Z3 is the only minimal backend target and Toetra should remain backend-agnostic before lowering.

## Impact on Toetra

IR2 is architecturally required for the full end-to-end pipeline, even if it is not part of the first implemented compiler slice yet.
