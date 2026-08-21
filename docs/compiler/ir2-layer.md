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
- non-blocking diagnostics;
- exact source-to-IR point mappings;
- the deduplicated set of required `(model, point, target)` evaluations;
- the complete ordered quantifier structure and alternation depth.

## Verification semantics

Universal and non-existential scopes use refutation:

```text
VC = Γ ∧ ¬P
```

Existential scopes use satisfaction:

```text
VC = Γ ∧ P
```

Homogeneous universal and existential chains are lowered to quantifier-free refutation or satisfaction bodies. Alternating chains retain their complete ordered binders, require native/advanced quantifier support, and are rejected by capability routing before solver translation when the selected backend cannot execute them soundly.

## Assumption aggregation

IR2 currently aggregates:

- domain assumptions generated from `ScopeIR.domain`;
- model assumptions produced by compiler lowering from Model IR;
- externally supplied backend-neutral assumptions;
- inline-anchor equality facts carrying exact point identity and source provenance.

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
- native quantifier and alternation needs;
- point count and anchor count;
- required model-evaluation count;
- binder sequence and alternation depth.

The backend router compares these requirements with a concrete capability declaration before translation.

## Diagnostics

IR2 diagnostics are non-blocking structural warnings. Evaluation-driven ModelBridge normally emits no model equation for a point-only property. Legacy or manually injected disconnected assumptions still produce `IR2_MODEL_OUTPUT_NOT_REFERENCED`, while missing, duplicate, or unrequested structured equations use the `MODEL_EVALUATION_*` family.

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

## Model-semantic quantities

P21.5 allows IR2 to carry framework-neutral internal model quantities produced
by semantic lowering. Their presence is exposed through
`requires_model_semantic_quantities`, and deterministic lowering evidence remains
attached to the task. The Z3 numeric-affine profile now declares and implements
this capability for affine internal quantities; other backends must still opt in
explicitly before routing can select them.
