# IR2 Layer

> Status: Implemented / stabilizing  
> Scope: Backend-neutral aggregation, normal forms, requirements and diagnostics

## Purpose

IR2 converts an NNF IR1 task into a backend-neutral verification task containing:

- the user specification `P`;
- provenanced assumptions `Γ`;
- verification semantics;
- a selected NNF, CNF or DNF verification condition;
- backend requirements;
- non-blocking diagnostics.

## Verification semantics

Universal and non-existential scopes use refutation:

```text
VC = Γ ∧ ¬P
```

Existential scopes use satisfaction:

```text
VC = Γ ∧ P
```

No native quantifier currently reaches the backend. The quantified scope is preserved as metadata while the verification condition is quantifier-free.

## Assumption aggregation

IR2 currently aggregates:

- domain assumptions generated from `ScopeIR.domain`;
- model assumptions produced by a `ModelEncoder`;
- externally supplied backend-neutral assumptions.

Each assumption carries:

- a source enum;
- an NNF formula;
- a description;
- provenance metadata.

## Domain lowering

Intervals expand into one or two comparisons with exact boundary operators. Numeric finite sets become membership disjunctions. Symbolic finite-set members remain explicit and trigger a symbolic-category requirement.

## Normal forms

IR2 supports:

- `NNFFormulaIR2`;
- `CNFFormulaIR2`;
- `DNFFormulaIR2`.

Boolean conversion changes grouping and literal polarity but treats each scalar comparison as an atomic predicate. Recursive scalar structure and specification-constant provenance are preserved.

## Requirements

`IR2Requirements` reports, among other fields:

- boolean and comparison needs;
- model and domain assumptions;
- verification semantics;
- normal form;
- affine, nonlinear and symbolic-division arithmetic;
- required scalar sorts;
- finite-set membership;
- symbolic categories;
- native quantifier needs.

The backend router compares these requirements with a concrete capability declaration before translation.

## Diagnostics

IR2 diagnostics are non-blocking structural warnings. For example, model assumptions combined with a property that never references a model output produce `IR2_MODEL_OUTPUT_NOT_REFERENCED`.

Backend result diagnostics are separate because they depend on solver execution. Vacuity detection therefore belongs to the Z3 runner rather than IR2 construction.

## Invariants

IR2 must not:

- import or construct solver-native expressions;
- lose scalar-expression or constant provenance;
- silently approximate unsupported arithmetic;
- select a backend by mutating the task;
- treat an unsupported capability as a parser error.

## Remaining work

Future IR2 work includes:

- richer simplification and redundancy analysis;
- explicit equivalence/equisatisfiability metadata for advanced transformations;
- unsat-core and proof-trace mappings;
- additional assumption sources;
- optimizer policies for large CNF/DNF expansions.
