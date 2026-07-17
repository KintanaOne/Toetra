# Verification Task IR2

> Status: Implemented for the numeric-affine V1 profile

`VerificationTaskIR2` is the complete backend-neutral verification request.

## Point-aware structure

A task exposes:

```text
property_type
scope / canonical restriction
specification formula
verification condition
assumptions
requirements
point_mappings
model_evaluations
quantifier_structure
provenance
```

`point_mappings` preserves every point identity and binding kind. `model_evaluations` contains exactly the distinct `(model, point, target)` evaluations referenced by the property. A property that never refers to `target` requests no model equation.

## Quantifier structure

IR2 records the ordered binder sequence and alternation depth. Homogeneous chains are executable in the initial profile:

```text
forall, forall  → universal refutation
exists, exists  → existential witness search
```

Alternating sequences are not flattened. They set `requires_quantifier_alternation` and are rejected by the current Z3 capability profile before translation.

## Assumptions

Assumptions retain structured provenance and point ownership:

- typed domain bounds;
- inline or runtime-resolved anchor facts;
- one model equation per required evaluation;
- future semantic or model assumptions.

A referenced anchor must be resolved before IR2. It may never reach the solver as an unconstrained symbolic point.

## Verification semantics

Universal properties use refutation:

```text
Γ ∧ R ∧ ¬P
```

Existential properties use satisfaction:

```text
Γ ∧ R ∧ P
```

where `Γ` contains domains, concrete anchor facts, and model equations, and `R` is the canonical restriction.

## Requirements

Requirements include scalar sorts, normal form, point count, anchor count, model-evaluation count, binder sequence, alternation depth, neighborhood needs, and native-quantifier requirements. Routing uses these requirements before backend execution.

## Invariants

- point identity is never inferred from an entity string;
- distinct points produce distinct evaluations;
- repeated target references are deduplicated;
- every requested model evaluation has exactly one connected model equation;
- no unrequested model equation is accepted;
- unsupported alternation is rejected before solver translation.
