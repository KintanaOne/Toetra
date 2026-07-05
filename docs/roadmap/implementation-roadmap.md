# Implementation Roadmap

> Status: Active  
> Scope: FORML implementation planning

## Purpose

This roadmap describes the intended implementation progression toward a functional FORML V1.

The goal is to avoid premature multi-backend complexity while preserving the architecture required for future extension.

## V1 principle

The first functional V1 should prove the full Z3-based end-to-end path.

```text
.forml + model
→ semantic validation
→ IR1
→ IR2
→ assertion aggregation
→ lowering
→ Z3 query
→ verification result
```

## Phase 0 — Documentation and architecture freeze

Goal:

```text
Clarify the target architecture and contracts before completing the end-to-end implementation.
```

Key outputs:

- MkDocs structure,
- architecture overview,
- compiler pipeline docs,
- ModelBridge docs,
- IR docs,
- contract docs,
- Miova integration docs,
- testing strategy,
- ADRs.

## Phase 1 — Compiler stabilization

Goal:

```text
Stabilize Source → CST → AST → SemanticValidatedAST → IR1.
```

Tasks:

- stabilize grammar casing,
- normalize vocabulary and enums,
- fix builder edge cases,
- stabilize semantic errors,
- ensure semantic annotations are consistently attached,
- ensure IR1 consumes resolved semantic bindings,
- add golden samples.

## Phase 2 — IR1 / NNF stabilization

Structural IR1 already exists. This phase is about making the normalization subphase real and testable.

Goal:

```text
Make IR1 a reliable normalized logical representation.
```

Tasks:

- define NNF invariant,
- implement De Morgan rewrites consistently,
- eliminate or normalize implication handling,
- preserve source traceability,
- add IR1 golden tests,
- add Hypothesis strategies for logical expressions.

## Phase 3 — IR2 / CNF-DNF

Goal:

```text
Introduce IR2 as the normal-form selection layer.
```

Tasks:

- define IR2 node model,
- implement CNF transformation,
- implement DNF transformation,
- document equivalence vs equisatisfiability,
- add normal-form tests,
- add mutation campaigns for logical rewrites.

## Phase 4 — ModelBridge integration

Goal:

```text
Connect ModelSchema to semantic validation and constraint preparation.
```

Tasks:

- stabilize loaders,
- stabilize detector,
- stabilize introspectors,
- define schema validation rules,
- validate DSL feature references against ModelSchema,
- prepare model constraint representation.

## Phase 5 — Assertion aggregation

Goal:

```text
Combine user assertions, semantic constraints, scope constraints, and model constraints.
```

Tasks:

- define AggregatedAssertionSet,
- track assertion provenance,
- detect contradictions,
- preserve traceability,
- add aggregation contract test.

## Phase 6 — Lowering and minimization

Goal:

```text
Prepare aggregated assertions for Z3 encoding.
```

Tasks:

- define LoweredQuery,
- simplify redundant constraints,
- normalize symbolic variables,
- minimize logical structure where safe,
- preserve diagnostic traceability.

## Phase 7 — Z3 backend V1

Goal:

```text
Implement the minimal Z3 backend path.
```

Tasks:

- define Z3 BackendQuery,
- encode supported IR constructs,
- run solver,
- return VerificationResult,
- classify SAT/UNSAT/UNKNOWN,
- expose diagnostics.

## Phase 8 — End-to-end tests

Goal:

```text
Validate the complete V1 path.
```

Tasks:

- define golden end-to-end samples,
- test Source + Model → Z3 result,
- add property-based tests,
- add intelligent fuzzing,
- add Miova mutation campaigns.

## Post-V1

Post-V1 extensions include:

- ERAN backend,
- multi-backend orchestration,
- AutoFORML,
- runtime monitoring,
- richer model encodings,
- advanced optimization passes,
- proof/explanation layers.
