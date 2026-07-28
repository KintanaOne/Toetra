# Lowering and normal-form selection

> **Status:** Implemented lowering and guarded normal-form conversion
>
> **Scope:** IR1 model semantics through IR2 formula selection

The current pipeline has no generic “minimization” pass and no `LoweredQuery`
artifact. Two concrete mechanisms occupy the design space that older documents
grouped under that name:

1. model-semantic lowering rewrites public output observables;
2. IR2 selects and converts the verification condition to NNF, CNF, or DNF.

## Model-semantic lowering

`ModelSemanticLowerer` receives a `VerificationTask` and `ModelSchema`. When the
task contains a model-dependent observable, the selected semantic profile
returns:

- a canonical backend-neutral task;
- structured `SemanticLoweringEvidence`;
- exact or directed numeric threshold information;
- the conclusions allowed by the transformation.

The initial binary-logistic profile lowers:

- predicted-label equality and inequality;
- pairwise predicted-label equality and inequality;
- ordered class-probability comparisons.

The generated oriented decision quantity remains internal. Public report and
replay views retain the original label/probability intent.

## NNF normalization

After lowering, `NNFNormalizer`:

- removes implication;
- pushes negation toward atoms;
- applies De Morgan transformations;
- normalizes restrictions and the property query.

`NNFGuard` rejects a task that reaches IR2 without satisfying these invariants.

## IR2 formula selection

`NormalFormSelector` examines the NNF verification condition and
`IR2BuildContext`. The builder can:

- keep `NNFFormulaIR2`;
- convert to `CNFFormulaIR2`;
- convert to `DNFFormulaIR2`.

The CNF/DNF converters preserve literal polarity explicitly. Conversion cost is
bounded to prevent uncontrolled distributive expansion. The selected actual
form is recorded on the task and in provenance.

## What is not implemented

There is no general-purpose optimizer that performs arbitrary:

- algebraic simplification;
- redundant-constraint elimination;
- solver-independent minimization;
- model pruning;
- backend-specific rewriting before routing.

A contributor must not describe the absence of such an optimizer as an
incomplete V1 execution step. The supported routes are executable without it.
Future optimizations must preserve traceability, requirements, and semantics and
must be measured independently from correctness.

## Backend boundary

IR2 normal-form selection remains backend-neutral. The router may use normal
form and requirement metadata to choose a capable backend, but the selected
backend performs its own native translation only after routing.

## Contracts

- [Model semantic lowering](../contracts/model-semantic-lowering.md)
- [Lowering and minimization contract](../contracts/lowering-minimization.md)
- [IR1 to IR2](../contracts/ir1-to-ir2.md)
- [Numeric compatibility reporting](../contracts/numeric-compatibility-reporting.md)
