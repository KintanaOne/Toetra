# Contracts overview

> **Status:** Active contract index for `1.0.0rc4`
>
> **Scope:** compiler, model, IR, backend, evidence, and release boundaries

A contract states what a producer guarantees, what a consumer may rely on, what
must be preserved, and which layer owns rejection.

## Contracted pipeline

```text
.toetra source
→ CST
→ ProgramNode AST
→ semantically validated AST state
→ VerificationTask IR1
→ model-semantic lowering
→ NNF
→ VerificationTaskIR2 + assumptions
→ BackendRoute
→ backend-private translation
→ VerificationResult
→ VerificationReport / replay
```

ModelBridge contributes:

```text
model artifact
→ ModelSchema
→ Model IR construction
→ semantic profile + compiler model lowering
→ model AssumptionIR2 values
```

The [compiler pipeline contract](compiler-pipeline.md) defines the complete
artifact progression.

## Contract categories

| Category | Main contracts | Purpose |
|---|---|---|
| Syntax | [source to CST](source-to-cst.md), [CST to AST](cst-to-ast.md), [AST](ast-contract.md), [DSL information preservation](dsl-information-preservation.md) | preserve accepted source as typed structure without silent loss |
| Semantics | [AST to semantic](ast-to-semantic.md), [schema to semantic](schema-to-semantic.md), [type normalization](type-normalization.md) | resolve bindings, points, types, and compatibility |
| Declarative model outputs | [output observables](model-output-observables.md), [model semantic lowering](model-semantic-lowering.md), [binary profile](binary-classification-profile.md) | separate public intent from internal model quantities |
| Logical IR | [semantic to IR1](semantic-to-ir1.md), [IR1 to IR2](ir1-to-ir2.md), [assumption composition](assertion-aggregation.md) | preserve meaning while normalizing and building the verification condition |
| ModelBridge | [model to schema](model-to-schema.md), [Model IR](model-ir.md), [model constraints](model-constraints.md) | normalize model interface and computation, then lower requested model equations |
| Numeric/backend | [numeric registry](numeric-compatibility-registry.md), [IR to backend](ir-to-backend.md), [backend execution](backend-execution-contract.md) | qualify and execute a sound backend route |
| Evidence | [reporting and replay](output-reporting-and-replay.md), [provenance](verification-provenance.md) | retain source meaning, evidence, fingerprints, and concrete observations |
| Product/release | [public V1](public-v1-contract.md), [CLI and automation](cli-automation-contract.md), [execution overrides](execution-overrides.md), [repository](repository-contract.md), [public repository readiness](public-repository-readiness.md), [release engineering](release-engineering.md) | freeze supported facade, process automation, layout, public exposure, and artifacts |

## Implemented versus target contracts

Every contract carries a status. Use these terms consistently:

| Label | Meaning |
|---|---|
| Implemented and accepted | current code and tests exercise the boundary |
| Stabilizing | boundary exists; non-public internal details may still improve |
| Accepted target | decision is normative for future work but not current support |
| Deferred | intentionally outside the V1 route |
| Superseded | retained only as architectural history |

An accepted target cannot be cited as evidence that a route executes today. The
[public V1 profile](../public-v1-profile.md) remains authoritative for complete
end-to-end support.

## Preservation principles

Across every implemented boundary:

- every information-bearing accepted construct is preserved until its owning boundary or rejected explicitly;

- quantified and point identities remain explicit;
- interval boundary kinds and finite-set meaning are preserved;
- scalar expressions are typed rather than flattened to text;
- model-dependent observables are rewritten only by the semantic-lowering
  boundary;
- assumptions remain distinguishable from the source property;
- unsupported arithmetic or numeric meaning is rejected, not approximated
  silently;
- `forall` and `exists` use distinct condition/result semantics;
- backend-native objects appear only after routing;
- reports retain source intent even when canonical constraints differ.

## Conceptual versus runtime names

Early contracts and ADRs used design labels such as `SemanticValidatedAST`,
`AggregatedAssertionSet`, `LoweredQuery`, or `BackendQuery`. In the as-built
pipeline these correspond respectively to:

| Design label | Implemented representation |
|---|---|
| semantic AST | validated `ProgramNode` state plus semantic context |
| aggregated assertion set | assumptions and verification condition inside `VerificationTaskIR2` |
| lowered query | model-semantically lowered/normalized task |
| backend query | adapter-private translation such as `Z3Translation` |

Current contributor documentation must use the implemented representation when
describing code.

## Cross-cutting contracts

- [Specification constants](specification-constants.md)
- [Point binding and evaluation](point-binding-and-evaluation.md)
- [Quantified domains and scalar expressions](quantified-domain-scalar-expressions.md)
- [Errors](errors.md)
- [Mutation boundaries](mutation-boundaries.md)
- [Generated numeric compatibility matrices](../generated/numeric-compatibility-matrices.md)
