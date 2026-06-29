# IR2 Normal Forms

> Status: Planned / Architecturally Required  
> Implementation: Not implemented yet  
> Scope: CNF, DNF, and backend-preparation logical forms

## Purpose

IR2 is the planned logical layer after IR1.

Its role is to transform IR1-NNF into the normal form required by the verification strategy.

IR1 answers:

```text
What is the normalized logical meaning?
```

IR2 answers:

```text
Which normal form should be used for verification?
```

---

## Why IR2 Exists

Different verification strategies need different logical shapes.

A solver-oriented backend may prefer conjunctive clauses.

A scenario exploration engine may prefer explicit cases.

A counterexample search strategy may need a form that exposes branches.

IR2 prevents these concerns from being mixed into IR1 or backend lowering.

---

## Supported Target Forms

### CNF

Conjunctive Normal Form represents logic as a conjunction of disjunctions.

```text
(A OR B) AND (C OR D)
```

CNF is useful for:

- SAT/SMT-style reasoning,
- clause-based solving,
- global consistency checking,
- solver-oriented simplification.

---

### DNF

Disjunctive Normal Form represents logic as a disjunction of conjunctions.

```text
(A AND B) OR (C AND D)
```

DNF is useful for:

- scenario exploration,
- case splitting,
- counterexample generation,
- mutation-driven boundary exploration,
- explaining alternative satisfaction paths.

---

## Normal Form Selection

IR2 should eventually support normal form selection based on:

- requested backend,
- property type,
- query shape,
- model constraints,
- strategy selected by orchestration,
- performance constraints,
- explainability needs.

Example:

| Need | Preferred Form |
|---|---|
| SMT solving | CNF-like or solver-native form |
| Case exploration | DNF |
| Counterexample search | DNF or mixed form |
| Global contradiction detection | CNF |
| Human explanation | DNF may be more readable |

---

## Equivalence vs Equisatisfiability

IR2 must explicitly track whether transformations preserve full logical equivalence or only equisatisfiability.

This distinction matters when transformations introduce helper variables or auxiliary clauses.

| Guarantee | Meaning |
|---|---|
| Semantic equivalence | The transformed expression has the same truth value in all contexts. |
| Equisatisfiability | The transformed expression is satisfiable exactly when the original is satisfiable, but may not be truth-equivalent under all assignments. |

For FORML, this guarantee should be stored or documented as part of the IR2 transformation contract.

---

## IR2 Input Contract

IR2 consumes IR1-NNF.

Input assumptions:

- no raw DSL syntax,
- semantic bindings are resolved,
- negations are normalized,
- implications are eliminated or explicitly handled,
- logical tree is structurally valid.

---

## IR2 Output Contract

IR2 should produce a representation that includes:

- selected normal form,
- transformed logical expression,
- preservation guarantee,
- traceability metadata,
- transformation diagnostics,
- optional strategy metadata.

Conceptual shape:

```text
IR2NormalForm
├── form = CNF | DNF | native | mixed
├── expression
├── preservation = equivalence | equisatisfiability
├── origin_trace
└── diagnostics
```

---

## What IR2 Does Not Do

IR2 should not:

- load models,
- inspect ML frameworks,
- encode solver objects,
- perform backend execution,
- own runtime monitoring,
- decide user-facing verification results.

IR2 prepares logic. It does not run verification.

---

## Relationship with Assertion Aggregation

IR2 may be applied before or during assertion aggregation depending on design.

Two valid strategies are possible:

### Strategy A — Normalize then aggregate

```text
IR1 → IR2 → aggregate with model constraints
```

Useful when user DSL assertions should be normalized independently.

### Strategy B — Aggregate then normalize

```text
IR1 + model constraints → aggregate → IR2
```

Useful when model constraints affect the best normal form.

The current target architecture favors this conceptual sequence:

```text
IR1 → IR2 → Assertion Aggregation → Lowering
```

but this remains an architectural decision that should be validated through implementation.

---

## Relationship with Miova

IR2 is a critical mutation target.

Miova can challenge:

- CNF/DNF preservation,
- invalid clause structures,
- malformed transformations,
- incorrect distribution rules,
- loss of traceability,
- equivalence violations,
- unsupported logical nodes.

---

## Summary

IR2 is the layer where FORML chooses the logical shape needed for verification.

It is not yet implemented, but it is architecturally required for the end-to-end FORML pipeline.
