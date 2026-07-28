# V1 Implementation Roadmap

> Status: Complete — historical plan through Patch 21
>
> Scope: delivered V1 compiler, runtime, and binary-classification work

This file preserves the implementation sequence used to reach the V1 release
candidate. It is not a current support statement or an active plan. Use the
[public V1 profile](../../public-v1-profile.md) for executable support and the
[active implementation roadmap](../../roadmap/implementation-roadmap.md) for
remaining work.

## Purpose

This roadmap describes the intended implementation progression toward a functional Toetra V1.

The goal is to avoid premature multi-backend complexity while preserving the architecture required for future extension.

## V1 principle

The first functional V1 should prove the full Z3-based end-to-end path.

```text
.toetra + model
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
- add aggregation contract tests.

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
- AutoToetra,
- runtime monitoring,
- richer model encodings,
- advanced optimization passes,
- proof/explanation layers.

---

## Documentation-First Language Migration

The implementation chantier for explicit quantified bindings, typed domains, scalar arithmetic and specification constants is complete through Patch 08. The sequence below is now a historical record of the delivered gates:

```text
1. EBNF and Lark grammar
2. parser golden tests
3. AST node model and builder
4. semantic scope/binding/domain/type validation
5. IR1 scalar and domain representation
6. IR2 domain assumptions, provenance and requirements
7. backend capabilities and initial Z3 numeric-affine translation
8. universal/existential result interpretation, result diagnostics and vacuity detection
9. final end-to-end golden and documentation status consolidation
```

Each delivered step follows the corresponding gate in `docs/testing/language-evolution-test-matrix.md`.

### Delivered implementation boundary

The completed initial profile includes:

- required identifiers for `forall` and `exists`;
- exact binding with no explicit-entity alias fallback;
- all four interval boundary combinations;
- numeric and symbolic finite-set representation;
- scalar expression AST/IR;
- numeric affine execution in Z3;
- structured rejection of nonlinear and categorical requests not yet supported.

Language representation remains broader than the executable Z3 profile. Capability mismatch is reported before solver execution, and parser acceptance alone never implies backend support. The next language chantier concerns richer scope and anchor semantics rather than unfinished scalar arithmetic infrastructure.

## User-facing Runtime and Reporting Consolidation

The usability chantier following the numeric-affine compiler profile is complete:

```text
Patch 09  — executable affine demonstration
Patch 10  — backend-neutral results and report model
Patch 11  — shared text rendering and versioned JSON
Patch 12  — public verify(...) API and VerificationSession
Patch 12.1 — self-contained user-script demonstration
Patch 13  — HTML/Jupyter rendering and credit-risk notebook
Patch 14  — public facade, normalized values and automatic replay
```

The public path is now:

```text
.toetra + serialized model + optional reference dataset
→ verify(...)
→ VerificationSession
→ text / JSON / HTML / Jupyter / counterexample replay
```

This closes the current scalar-arithmetic, domain, affine-Z3 and user-output
chantier. The next language chantier is the redesign of anchors, `at`,
`check_at`, multiple/nested quantified entities and their scope semantics.


## Patch 15 — First-Class Points and Indexed Evaluations

Patch 15-D1 froze the target language and cross-layer contract for anchors,
ordered binders, restrictions, point-indexed targets, per-point model equations,
and multi-point evidence.

Patch 15-D2 freezes the implementation sequence. The authoritative detailed
plan is:

```text
history/roadmaps/point-binding-evaluation-implementation-roadmap.md
```

Patches 15.1 through 15.9 are complete: the target surface reaches a faithful CST, a point-aware AST, immutable global anchor symbols, lexical point frames, deterministic default-point resolution, canonical restriction/scope-sugar semantics, point-aware IR1 and IR2 requirements with safe alternation gating, evaluation-driven per-point ModelBridge equations, and collision-free multi-point Z3 execution with reversible symbol mappings. The next integration gate is Patch 15.10.

The sequence is:

```text
15.1  Grammar and parser [complete]
15.2  AST and builder [complete]
15.3  Global anchors and composed point environment [complete]
15.4  Lexical binders, default points, and indexed targets [complete]
15.5  Restrictions, neighborhoods, and scope sugar [complete]
15.6  Point-aware IR1 [complete]
15.7  Point-aware IR2 and capability requirements [complete]
15.8  Per-point ModelBridge equations [complete]
15.9  Z3 point mapping and multi-point execution [complete]
15.10 Anchor resolution and runtime API [next]
15.11 Grouped reporting and multi-point replay
15.12 End-to-end consolidation and migration closure
```

The detailed roadmap owns patch dependencies, acceptance-matrix assignments,
non-goals, migration policy, and stop-the-line conditions. This global roadmap
must not be used to bypass those finer-grained gates.

## Patch 21 — Declarative Binary Classification

> Status: P21.0 specification freeze accepted; implementation pending

The next chantier introduces typed output observables and a framework-neutral
binary logistic classification profile. A direct fitted sklearn
`LogisticRegression` will be the first concrete bridge, but neither sklearn nor
Z3 defines the public language semantics.

The normative patch sequence, debts, and gates are maintained in the
[Binary Classification Implementation Roadmap](binary-classification-implementation-roadmap.md),
with stable acceptance IDs in the
[Binary Classification Test Matrix](../../testing/binary-classification-test-matrix.md).

The current `1.0.0rc1` public profile remains unchanged until P21.11.
