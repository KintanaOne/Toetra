# IR2 Layer

> Status: P0 / Planned / Architecturally Required  
> Scope: IR1 to clause-oriented or case-oriented normal forms  
> Implementation: Not yet implemented  
> Audience: IR authors, backend authors, solver integration authors

## Purpose

IR2 is the planned logical representation layer after IR1.

It answers the question:

```text
Which normal form should this verification task use before aggregation and backend preparation?
```

IR2 is responsible for CNF, DNF, and future normal forms depending on verification needs.

---

## Position in the Pipeline

```text
IR1 / NNF
    ↓
IR2 / CNF-DNF
    ↓
Assertion Aggregation
```

IR1 performs early logical normalization, including De Morgan and NNF.

IR2 selects and produces forms such as CNF or DNF.

---

## Why IR2 Exists

IR1 is a normalized logical tree.

That is not always the best representation for solving, minimization, counterexample search, or backend lowering.

IR2 exists to prepare the logical structure for downstream needs.

---

## Target Normal Forms

### CNF

Conjunctive Normal Form represents logic as a conjunction of clauses.

Conceptually:

```text
(A OR B) AND (C OR D) AND ...
```

CNF is useful for:

- SAT/SMT-style solving;
- global consistency checking;
- clause-level simplification;
- unsat core analysis;
- backend preparation for solvers that prefer conjunctive constraints.

---

### DNF

Disjunctive Normal Form represents logic as a disjunction of cases.

Conceptually:

```text
(A AND B) OR (C AND D) OR ...
```

DNF is useful for:

- scenario exploration;
- case splitting;
- counterexample search;
- mutation-driven boundary analysis;
- explaining alternative satisfaction paths.

---

## Normal Form Selection

IR2 may be selected by:

- explicit user configuration;
- property type;
- backend capability;
- solver strategy;
- query complexity;
- counterexample generation mode;
- Miova campaign objective.

Example:

| Need | Likely IR2 Form |
|---|---|
| SMT solving | CNF or solver-native conjunctions |
| Counterexample exploration | DNF |
| Boundary discovery | DNF or hybrid form |
| Global constraint consistency | CNF |
| Human explanation | DNF or structured original form |

---

## Equivalence Policy

IR2 transformations must declare their preservation semantics.

| Transformation Type | Required Guarantee |
|---|---|
| Simple De Morgan / distribution | Logical equivalence |
| Tseitin-style encoding | Equisatisfiability, not strict equivalence |
| Simplification | Logical equivalence or explicit approximation |
| Backend-specific normalization | Backend result preservation |

The distinction between logical equivalence and equisatisfiability is important and must be visible in IR2 metadata.

---

## Proposed IR2 Artifact

The exact implementation is open, but IR2 should likely expose an artifact similar to:

```text
NormalizedVerificationTask
    property_type
    scope
    normal_form
    clauses_or_cases
    preservation_mode
    traceability
    backend_hint
```

Where `normal_form` may be:

```text
NNF
CNF
DNF
HYBRID
BACKEND_NATIVE
```

---

## Traceability Requirement

IR2 must preserve traceability to IR1.

Every generated clause or case should be traceable back to:

- original property;
- original assertion;
- original IR1 node;
- semantic entity or feature;
- transformation rule.

This is critical for diagnostics, explanations, minimization, and Miova validation.

---

## What IR2 Must Not Do

IR2 must not:

- load ML models;
- inspect raw sklearn/XGBoost objects;
- produce Z3 expressions directly;
- execute verification;
- hide lossy transformations;
- drop traceability.

---

## Relation to Assertion Aggregation

IR2 produces normalized logical forms that are ready to be aggregated with:

- other property assertions;
- semantic constraints;
- model-derived constraints;
- backend capability constraints.

Aggregation should consume IR2, not raw AST and preferably not raw IR1 when clause/case structure is needed.

---

## Relation to Miova

Miova can challenge IR2 by mutating:

- clauses;
- cases;
- normal form metadata;
- preservation mode;
- traceability links;
- operators;
- atomic predicates.

Expected checks include:

- CNF shape validity;
- DNF shape validity;
- equivalence/equisatisfiability contract;
- no orphaned generated clauses;
- no backend object leakage.
