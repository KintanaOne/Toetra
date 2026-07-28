# Lowering and normal-form contract

> **Status:** Implemented lowering; no generic minimizer
>
> **Scope:** model-semantic IR1 rewriting and IR2 formula selection

## Implemented transformations

The current pipeline implements:

1. model-semantic lowering from public output observables to canonical
   model-family constraints;
2. NNF normalization;
3. guarded NNF/CNF/DNF selection and conversion.

It does not produce a `LoweredQuery` object.

## Model-semantic preservation

Every observable rewrite must:

- use a registered model-family profile;
- preserve source intent separately;
- emit deterministic lowering evidence;
- declare exact or conservative numeric meaning;
- record permitted conclusions;
- reject unsupported operators, labels, thresholds, or decision policies.

Lowering that introduces Boolean structure occurs before final NNF.

## Normal-form preservation

NNF conversion eliminates implication and pushes negation to atoms while
preserving semantics.

CNF/DNF conversion may change structure but must preserve logical equivalence,
atom identity, literal polarity, point identity, and provenance. Conversion
cost is bounded; uncontrolled expansion is rejected or safely avoided according
to the build policy.

## No generic minimization claim

`1.0.0rc3` does not promise:

- arbitrary constant/algebraic folding;
- subsumption or redundant-constraint elimination;
- dead-branch pruning;
- solver-independent query minimization;
- backend-preparation rewrites outside an adapter.

Future optimizers require an explicit preservation contract and traceability.
They are optimizations, not missing correctness steps in the supported V1 route.

## Backend boundary

The result remains `VerificationTaskIR2`. Backend-native translation occurs only
after capability, numeric, and execution-policy qualification.
