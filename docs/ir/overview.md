# Intermediate representations overview

> **Status:** Implemented for `1.0.0rc4`
>
> **Scope:** IR1, model-semantic lowering, NNF, and IR2

Toetra uses two backend-neutral intermediate-representation layers:

```text
validated ProgramNode
→ VerificationTask (IR1)
→ model-semantic lowering
→ NNF VerificationTask
→ VerificationTaskIR2
→ backend routing
```

Backend-native translations are adapter-private and are not a third shared IR.

## IR1: declarative intent

IR1 retains the property as a backend-independent task:

- `VerificationTask`;
- `ScopeIR`, domains, points, restrictions, and binders;
- `QueryIR`;
- logical and scalar nodes;
- `ModelEvaluationIR` identities;
- public output-observable expressions;
- optional backend hint.

IR1 answers:

> What typed logical property did the user declare?

Model-dependent observables can remain in IR1 because their meaning depends on
the normalized model family. No solver or framework estimator object is
permitted.

## Model-semantic lowering

The schema-aware path rewrites supported output observables into canonical IR1
constraints. The result is still a `VerificationTask`, accompanied by lowering
evidence.

This step answers:

> What mathematical relation represents this public observable for the selected
> model family?

It precedes final NNF because a rewrite can introduce conjunctions,
disjunctions, or strict/non-strict decision boundaries.

## NNF invariant

`NNFNormalizer` produces IR1 in negation normal form:

- implication is eliminated;
- negation occurs only above atomic predicates;
- point, model-evaluation, and source meaning are preserved.

NNF is an invariant of the task passed to `IR2Builder`, not a distinct top-level
task class.

## IR2: executable backend-neutral task

`VerificationTaskIR2` contains:

- normalized source property as `spec_formula`;
- typed `AssumptionIR2` values;
- executable verification condition;
- actual `NormalFormKind`;
- `VerificationSemantics`;
- `IR2Requirements`;
- point mappings and model evaluations;
- quantifier structure;
- diagnostics and metadata;
- lowering evidence and original source formula.

IR2 answers:

> What complete, qualified logical condition must a backend execute?

Formula variants are explicit:

- `NNFFormulaIR2`;
- `CNFFormulaIR2`;
- `DNFFormulaIR2`.

## Assumption composition

Domain, anchor, and model constraints are represented as typed assumptions
inside `VerificationTaskIR2`. The task also contains the composed verification
condition. There is no separate `AggregatedAssertionSet`.

For universal refutation the condition is `Γ ∧ ¬P`; for existential witness
search it is `Γ ∧ P`.

## Backend boundary

The router consumes IR2 requirements and produces a `BackendRoute`. The selected
adapter then creates a backend-private native translation. Z3 uses
`Z3Translation`.

There is no shared `LoweredQuery` or `BackendQuery` Python type in the current
pipeline. Those names in older design records describe conceptual stages, not
runtime artifacts.

## Layer invariants

| Layer | Must preserve | Must exclude |
|---|---|---|
| IR1 | source intent, point identity, types, observable identity | Lark nodes, backend objects |
| lowered IR1 | source trace, canonical model-family meaning, evidence | unresolved supported observables |
| NNF IR1 | semantic equivalence and atom identity | implication, non-leaf negation |
| IR2 | assumptions, semantics, requirements, provenance | framework estimators, backend API objects |
| backend translation | all accepted IR2 meaning | unsupported/coerced requirements |

## Related documents

- [Verification task](verification-task.md)
- [Scope IR](scope-ir.md)
- [Logical IR](logical-ir.md)
- [IR1 NNF](ir1-nnf.md)
- [IR2 normal forms](ir2-normal-forms.md)
- [Assumptions and verification condition](aggregated-assertion-set.md)
- [Backend translation](backend-query.md)
