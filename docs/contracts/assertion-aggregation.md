# Assumption composition contract

> **Status:** Implemented and accepted
>
> **Scope:** property plus typed assumptions to IR2 verification condition

## Purpose

A user property `P` is not the complete solver condition. `IR2Builder` composes
it with typed assumptions `Γ` and explicit verification semantics inside
`VerificationTaskIR2`.

There is no separate `AggregatedAssertionSet` runtime class.

## Inputs

- normalized user property;
- domain assumptions;
- resolved anchor assumptions;
- model assumptions;
- optional explicitly supplied internal assumptions;
- universal-refutation or existential-witness semantics;
- source and lowering provenance.

Every assumption is an `AssumptionIR2` with a source, NNF formula, optional
description, and metadata.

## Composition

Universal:

```text
Γdomain ∧ Γanchor ∧ Γmodel ∧ ¬P
```

| Backend outcome | Toetra meaning |
|---|---|
| UNSAT | `PROVED`, subject to compatibility policy |
| SAT | `COUNTEREXAMPLE` |
| UNKNOWN/limit | `UNKNOWN` |

Existential:

```text
Γdomain ∧ Γanchor ∧ Γmodel ∧ P
```

| Backend outcome | Toetra meaning |
|---|---|
| SAT | `WITNESS`, subject to compatibility policy |
| UNSAT | `NO_WITNESS` |
| UNKNOWN/limit | `UNKNOWN` |

## Required separation

The completed task must retain:

- normalized property as `spec_formula`;
- assumptions as typed individual entries;
- composed executable `verification_condition`;
- `VerificationSemantics`;
- source property before model-semantic lowering;
- assumption and lowering provenance.

## Domain and model rules

- interval lower/upper predicates are conjoined;
- finite-set members are disjoined and entries are conjoined;
- open/closed boundaries are preserved;
- encoders emit exactly one model equation per requested evaluation;
- assumptions never stand in for backend capability checks.

## Vacuity

An inconsistent `Γ` makes the admissible set empty. The backend runner may issue
a separate assumptions-only diagnostic within the total execution budget.
Universal UNSAT caused by inconsistent assumptions must not be described as an
ordinary non-vacuous proof without that evidence.

## Failures

Composition rejects invalid semantics, malformed assumption sources, wrong point
identities, or a condition that fails IR2 validation. Backend incompatibility is
owned by routing.
