# FORML Documentation Roadmap

> Status: P0 documentation baseline  
> Scope: Documentation architecture and rewrite plan  
> Purpose: Define every document to produce, its location, priority, status, and reason for existence

This roadmap defines the documentation structure for FORML.

The goal is not only to document what is already implemented. The goal is to document the end-to-end architecture in a way that remains truthful today and stable tomorrow.

Each document should clearly distinguish:

- what is currently implemented,
- what is stabilizing,
- what is planned and architecturally required,
- and what belongs to future research directions.

## Documentation status levels

| Status | Meaning |
|---|---|
| `implemented` | The subsystem exists in code and has a usable implementation. |
| `stabilizing` | The subsystem exists but APIs, contracts, naming, or invariants still need cleanup. |
| `planned` | The subsystem is not implemented yet but is required by the target end-to-end architecture. |
| `research-direction` | The idea is part of the long-term vision but should not be presented as a near-term guarantee. |
| `external` | The concern is handled by another project, mainly Miova. |

## Priority levels

| Priority | Meaning |
|---|---|
| P0 | Required to understand, stabilize, or implement the end-to-end FORML pipeline. |
| P1 | Important for maintainability, contributors, and future extension. |
| P2 | Useful for onboarding, tutorials, examples, or long-term product documentation. |

## P0 documentation goals

P0 documentation must make the following architecture explicit:

```text
.forml source
    ↓
CST
    ↓
AST
    ↓
SemanticValidatedAST
    ↓
IR1 / NNF
    ↓
IR2 / CNF-DNF
    ↓
Aggregated Assertion Set
    ↓
ModelBridge-derived constraints
    ↓
Lowering / Minimization
    ↓
Backend Query
    ↓
Verification Runtime
```

P0 documentation must also explain how Miova challenges FORML artifacts without being part of the normal runtime verification path.

---

# 1. Root documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P0 | Home | `docs/index.md` | stabilizing | Present FORML, its purpose, architecture, and current state. | First page readers see; must explain FORML without requiring code knowledge. | Users, recruiters, contributors, future self. |
| P0 | Documentation Roadmap | `docs/docs-roadmap.md` | stabilizing | Define the entire documentation plan. | Prevent fragmented docs and make the rewrite progressive. | Maintainer, contributors. |

---

# 2. Architecture documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P0 | Architecture Overview | `docs/architecture/overview.md` | stabilizing | Explain current and target FORML architecture. | Provides the main system-level mental model. | Technical readers, contributors. |
| P0 | Pipeline Views | `docs/architecture/pipeline-views.md` | planned | Present global, DSL, ModelBridge, logical, backend, runtime, and Miova views. | Preserves the original multi-view architecture while updating terminology. | Architects, contributors. |
| P0 | Runtime Flow | `docs/architecture/runtime-flow.md` | planned | Explain the end-to-end flow from `.forml` and model artifact to verification result. | Needed to understand how all subsystems connect. | Developers, future users. |
| P0 | Status Matrix | `docs/architecture/status-matrix.md` | stabilizing | Separate implemented, stabilizing, planned, and research-direction components. | Prevents overclaiming while documenting the target architecture. | Everyone. |
| P1 | Dependencies | `docs/architecture/dependencies.md` | planned | Explain internal and external dependencies. | Helps packaging, setup, and future backend support. | Maintainers. |
| P1 | C4 Context | `docs/architecture/c4-context.md` | planned | Show FORML in its external ecosystem. | Useful for readers who need a system context view. | Recruiters, architects, contributors. |
| P1 | C4 Container | `docs/architecture/c4-container.md` | planned | Show major FORML containers/subsystems. | Clarifies package and subsystem boundaries. | Contributors. |
| P1 | Compiler Components | `docs/architecture/c4-component-compiler.md` | planned | Detail compiler components. | Makes parser/builder/semantic/IR relations visible. | Developers. |
| P1 | ModelBridge Components | `docs/architecture/c4-component-model-bridge.md` | planned | Detail ModelBridge components. | Clarifies loader/detector/introspector/schema responsibilities. | Developers. |
| P1 | Logical Verification Components | `docs/architecture/c4-component-logical-pipeline.md` | planned | Detail IR1, IR2, aggregation, lowering, backend query. | Required once logical pipeline implementation grows. | Developers. |

---

# 3. Language documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P1 | Language Overview | `docs/language/overview.md` | planned | Introduce the FORML DSL. | Gives readers a friendly entry to the language. | Users, contributors. |
| P1 | Grammar | `docs/language/grammar.md` | implemented / stabilizing | Document the grammar and its Lark representation. | Grammar is the source boundary of the compiler. | Developers. |
| P1 | Vocabulary | `docs/language/vocabulary.md` | stabilizing | Document official properties, problems, functions, metrics, backends, operators. | Avoids ambiguity between grammar tokens and enum values. | Developers, users. |
| P1 | Syntax | `docs/language/syntax.md` | stabilizing | Explain concrete syntax. | Needed for writing valid `.forml` files. | Users. |
| P1 | Properties | `docs/language/properties.md` | stabilizing | Explain ROBUSTNESS, STABILITY, FAIRNESS, MONOTONICITY, BOUND, LOGIC. | Properties are the user-facing semantic entry point. | Users, developers. |
| P1 | Scopes | `docs/language/scopes.md` | stabilizing | Explain `at`, `check_at`, `pairwise`, `forall`, `exists`. | Scopes drive semantic context generation. | Users, developers. |
| P1 | Assertions | `docs/language/assertions.md` | stabilizing | Explain comparisons, logical operators, implication, problem functions. | Assertions are lowered to logical IR. | Users, developers. |
| P1 | Backends Syntax | `docs/language/backends.md` | planned | Explain `using z3(...)`, `using eran(...)`, etc. | Backend syntax must be separated from backend implementation. | Users. |
| P2 | Examples | `docs/language/examples.md` | planned | Provide valid and invalid examples. | Should be aligned with golden samples. | Users. |

---

# 4. Compiler documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P0 | Compiler Pipeline | `docs/compiler/pipeline.md` | stabilizing | Define the end-to-end compiler path. | Central technical document for the rewrite. | Developers. |
| P1 | Language Layer | `docs/compiler/language-layer.md` | stabilizing | Explain grammar, vocabulary, generator, and token normalization. | Prevents grammar/vocabulary drift. | Developers. |
| P1 | Parser Layer | `docs/compiler/parser-layer.md` | implemented / stabilizing | Explain source to CST. | Parser is the first compiler boundary. | Developers. |
| P1 | Builder Layer | `docs/compiler/builder-layer.md` | implemented / stabilizing | Explain CST to AST construction. | Builder defines AST integrity. | Developers. |
| P1 | AST Layer | `docs/compiler/ast-layer.md` | stabilizing | Explain AST node responsibilities and invariants. | Important because semantic annotations are attached later. | Developers. |
| P1 | Semantic Layer | `docs/compiler/semantic-layer.md` | implemented / stabilizing | Explain LHS validation, binding, logic validation, compatibility. | Semantic layer is the meaning boundary. | Developers. |
| P0 | IR1 Layer | `docs/compiler/ir1-layer.md` | implemented / stabilizing | Explain structural IR1 and its target NNF subphase. | IR1 is the current logical target; NNF is next. | Developers. |
| P0 | IR2 Layer | `docs/compiler/ir2-layer.md` | planned / critical | Explain planned CNF/DNF layer. | Required before advanced backend preparation. | Developers. |
| P0 | Assertion Aggregation | `docs/compiler/assertion-aggregation.md` | planned / critical | Explain aggregation of DSL, semantic, and model constraints. | Core junction before lowering. | Developers. |
| P0 | Lowering and Minimization | `docs/compiler/lowering-minimization.md` | planned / critical | Explain simplification, minimization, backend preparation. | Needed before backend-specific query generation. | Developers. |
| P0 | Backend Boundary | `docs/compiler/backend-boundary.md` | planned / critical | Define where FORML artifacts become backend-specific. | Prevents backend leakage into earlier layers. | Developers. |

---

# 5. ModelBridge documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P0 | ModelBridge Overview | `docs/model-bridge/overview.md` | partially implemented | Explain the model-side pipeline. | ModelBridge is required for model-aware verification. | Developers, users. |
| P1 | Model Loading | `docs/model-bridge/model-loading.md` | implemented / stabilizing | Explain pkl/joblib/json loading. | Loader contracts must be explicit. | Developers. |
| P1 | Model Detection | `docs/model-bridge/model-detection.md` | implemented / stabilizing | Explain sklearn/XGBoost detection. | Detection chooses introspector. | Developers. |
| P1 | Model Introspection | `docs/model-bridge/model-introspection.md` | implemented / stabilizing | Explain metadata extraction. | Introspection produces normalized schema. | Developers. |
| P0 | Model Schema | `docs/model-bridge/model-schema.md` | implemented / stabilizing | Document `ModelSchema` and `FeatureSchema`. | Schema is the bridge between model, semantic validation, and backend lowering. | Developers. |
| P0 | Model Constraints | `docs/model-bridge/model-constraints.md` | planned / critical | Explain future model-derived constraints. | Needed for aggregation and backend queries. | Developers. |
| P1 | Supported Frameworks | `docs/model-bridge/supported-frameworks.md` | stabilizing | Track sklearn, XGBoost, PyTorch, TensorFlow support. | Prevents unclear support claims. | Users, developers. |

---

# 6. Intermediate Representation documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P0 | IR Overview | `docs/ir/overview.md` | stabilizing | Explain why FORML uses IR layers. | IR is the backbone between semantics and backend. | Developers. |
| P0 | Verification Task | `docs/ir/verification-task.md` | implemented / stabilizing | Explain the top-level IR unit. | Current IR1 output is task-oriented. | Developers. |
| P1 | Scope IR | `docs/ir/scope-ir.md` | implemented / stabilizing | Explain local, pointwise, pairwise, quantifier scopes in IR. | Scope controls backend semantics. | Developers. |
| P0 | Logical IR | `docs/ir/logical-ir.md` | implemented / stabilizing | Explain ComparisonIR, AndIR, OrIR, NotIR, ImplyIR, ProblemIR. | Logical IR is transformed into NNF/CNF/DNF. | Developers. |
| P0 | IR1 NNF | `docs/ir/ir1-nnf.md` | planned / critical | Explain De Morgan and NNF responsibilities. | IR1 must have clear invariants before IR2. | Developers. |
| P0 | IR2 Normal Forms | `docs/ir/ir2-normal-forms.md` | planned / critical | Explain CNF/DNF and selection criteria. | Required for solver-oriented preparation. | Developers. |
| P0 | Aggregated Assertion Set | `docs/ir/aggregated-assertion-set.md` | planned / critical | Explain combined DSL + semantic + model constraints. | Central artifact before lowering. | Developers. |
| P0 | Backend Query | `docs/ir/backend-query.md` | planned / critical | Explain final backend-specific representation. | Defines what a backend receives. | Developers. |

---

# 7. Contract documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P0 | Contracts Overview | `docs/contracts/overview.md` | planned | Explain contract-oriented compilation. | Makes the architecture verifiable. | Developers. |
| P0 | Compiler Pipeline Contract | `docs/contracts/compiler-pipeline.md` | stabilizing | Define global compiler artifacts and boundaries. | Parent contract for all compiler layers. | Developers. |
| P0 | Source to CST | `docs/contracts/source-to-cst.md` | implemented / stabilizing | Define parser contract. | Required for grammar/parser testing. | Developers. |
| P0 | CST to AST | `docs/contracts/cst-to-ast.md` | implemented / stabilizing | Define builder contract. | Required for AST integrity. | Developers. |
| P0 | AST Contract | `docs/contracts/ast-contract.md` | stabilizing | Define AST invariants. | Prevents dynamic semantic attachment confusion. | Developers. |
| P0 | AST to Semantic | `docs/contracts/ast-to-semantic.md` | implemented / stabilizing | Define semantic validation contract. | Meaning boundary of the compiler. | Developers. |
| P0 | Semantic to IR1 | `docs/contracts/semantic-to-ir1.md` | implemented / stabilizing | Define lowering into IR1. | Must preserve semantic resolution. | Developers. |
| P0 | IR1 to IR2 | `docs/contracts/ir1-to-ir2.md` | planned / critical | Define CNF/DNF transformation contract. | Needed before backend preparation. | Developers. |
| P0 | Model to Schema | `docs/contracts/model-to-schema.md` | implemented / stabilizing | Define ModelBridge schema production. | Required for model-aware semantics. | Developers. |
| P0 | Schema to Semantic | `docs/contracts/schema-to-semantic.md` | planned / critical | Define how schema validates DSL references. | Required for feature-aware validation. | Developers. |
| P0 | Model Constraints | `docs/contracts/model-constraints.md` | planned / critical | Define model-derived constraint generation. | Required for aggregation. | Developers. |
| P0 | Assertion Aggregation | `docs/contracts/assertion-aggregation.md` | planned / critical | Define aggregation of all verification constraints. | Central end-to-end contract. | Developers. |
| P0 | Lowering and Minimization | `docs/contracts/lowering-minimization.md` | planned / critical | Define simplification/minimization guarantees. | Prevents unsafe logic rewriting. | Developers. |
| P0 | IR to Backend | `docs/contracts/ir-to-backend.md` | planned / critical | Define backend query boundary. | Backend-specific code depends on it. | Developers. |
| P0 | Errors | `docs/contracts/errors.md` | stabilizing | Define parser/build/semantic/model/IR/backend errors. | Error boundaries are currently important to clean. | Developers. |
| P0 | Type Normalization | `docs/contracts/type-normalization.md` | stabilizing | Define enum/dtype/string normalization. | Prevents grammar/enum mismatch bugs. | Developers. |
| P0 | Mutation Boundaries | `docs/contracts/mutation-boundaries.md` | planned / critical | Define how Miova mutates FORML artifacts. | Required for robust mutation campaigns. | Developers. |

---

# 8. Backend documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P1 | Backends Overview | `docs/backends/overview.md` | planned | Introduce backend concept. | Explains where solvers/verifiers fit. | Users, developers. |
| P1 | Backend Capabilities | `docs/backends/capabilities.md` | planned | Define capability matching. | Needed for future orchestration. | Developers. |
| P1 | Backend Orchestration | `docs/backends/orchestration.md` | planned | Explain backend selection strategy. | Basis of future AutoFORML. | Developers. |
| P1 | Z3 Backend | `docs/backends/z3.md` | planned / critical | Document first solver target. | Z3 is a likely first backend. | Developers. |
| P2 | ERAN Backend | `docs/backends/eran.md` | research-direction | Document future ERAN integration. | Useful but not immediate. | Developers. |
| P1 | Diagnostics | `docs/backends/diagnostics.md` | planned | Explain backend errors and unsupported cases. | Required for user-facing failures. | Users, developers. |

---

# 9. Runtime documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P2 | Runtime Overview | `docs/runtime/overview.md` | planned | Explain future runtime execution. | Needed once backend queries can execute. | Users, developers. |
| P2 | Verification Runtime | `docs/runtime/verification-runtime.md` | planned | Explain execution of backend queries. | Makes end-to-end concrete. | Developers. |
| P2 | Monitoring | `docs/runtime/monitoring.md` | research-direction | Explain future runtime monitoring. | Long-term architecture target. | Users, architects. |
| P2 | Results and Traces | `docs/runtime/results-and-traces.md` | planned | Explain outputs, diagnostics, traces. | Required for user interpretation. | Users, developers. |

---

# 10. Miova integration documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P0 | Miova Overview | `docs/miova/overview.md` | external / planned integration | Explain Miova's role around FORML. | Prevents confusion between FORML verification and Miova mutation. | Users, developers. |
| P0 | Artifact Boundaries | `docs/miova/artifact-boundaries.md` | planned / critical | Map FORML artifacts to Miova mutation targets. | Required for mutation campaigns. | Developers. |
| P0 | Mutation Campaigns | `docs/miova/mutation-campaigns.md` | planned / critical | Explain campaign strategy. | Converts Miova into practical FORML testing. | Developers. |
| P0 | Contract Testing | `docs/miova/contract-testing.md` | planned / critical | Explain how Miova validates layer contracts. | Main use case for Miova + FORML. | Developers. |
| P0 | Invariant Testing | `docs/miova/invariant-testing.md` | planned / critical | Explain state/transition invariants. | Makes compiler robustness measurable. | Developers. |
| P0 | Expected Failures | `docs/miova/expected-failures.md` | planned / critical | Explain expected rejection and failure classification. | Needed for mutation campaigns to be meaningful. | Developers. |

---

# 11. Testing documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P0 | Testing Strategy | `docs/testing/strategy.md` | planned / critical | Define test layers and priorities. | Required before large refactors. | Developers. |
| P1 | Unit Tests | `docs/testing/unit-tests.md` | planned | Explain unit test expectations. | Helps maintain local correctness. | Developers. |
| P0 | Compiler Contract Tests | `docs/testing/compiler-contract-tests.md` | planned / critical | Test layer boundaries. | Contracts must be executable. | Developers. |
| P0 | Golden Samples | `docs/testing/golden-samples.md` | planned / critical | Define stable DSL examples and expected outputs. | Required for end-to-end confidence. | Developers. |
| P0 | End-to-End Tests | `docs/testing/end-to-end-tests.md` | planned / critical | Define `.forml + model → result` tests. | Final proof of pipeline functionality. | Developers. |
| P0 | Miova Campaigns | `docs/testing/miova-campaigns.md` | planned / critical | Define mutation campaign tests. | Validates robustness, expected failures, and boundaries. | Developers. |

---

# 12. ADR documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P1 | ADR Overview | `docs/adr/overview.md` | planned | Explain ADR process. | Keeps design choices explicit. | Contributors. |
| P1 | ADR-0001 Compiler Pipeline | `docs/adr/ADR-0001-compiler-pipeline.md` | planned | Decide the compiler pipeline structure. | Foundational architecture decision. | Contributors. |
| P1 | ADR-0002 Layered Artifacts | `docs/adr/ADR-0002-layered-artifacts.md` | planned | Decide artifact boundaries. | Needed for compiler and Miova. | Contributors. |
| P1 | ADR-0003 AST vs Semantic AST | `docs/adr/ADR-0003-ast-vs-semantic-ast.md` | planned | Decide semantic annotation strategy. | Important current design tension. | Developers. |
| P1 | ADR-0004 Enum Normalization Boundary | `docs/adr/ADR-0004-enum-normalization-boundary.md` | planned | Decide normalization rules. | Prevents grammar/enum drift. | Developers. |
| P1 | ADR-0005 Semantic Annotations | `docs/adr/ADR-0005-semantic-annotations.md` | planned | Decide role of `SemanticAnnotations`. | Critical for semantic-to-IR. | Developers. |
| P1 | ADR-0006 IR1 NNF | `docs/adr/ADR-0006-ir1-nnf.md` | planned | Decide IR1 responsibilities. | Stabilizes current IR. | Developers. |
| P1 | ADR-0007 IR2 Normal Forms | `docs/adr/ADR-0007-ir2-normal-forms.md` | planned | Decide CNF/DNF strategy. | Stabilizes next IR layer. | Developers. |
| P1 | ADR-0008 ModelSchema as Bridge | `docs/adr/ADR-0008-modelschema-as-bridge.md` | planned | Decide ModelBridge contract. | Critical for model-aware verification. | Developers. |
| P1 | ADR-0009 Assertion Aggregation | `docs/adr/ADR-0009-assertion-aggregation.md` | planned | Decide aggregation model. | Central end-to-end decision. | Developers. |
| P1 | ADR-0010 Backend Boundary | `docs/adr/ADR-0010-backend-boundary.md` | planned | Decide backend query boundary. | Prevents backend leakage. | Developers. |
| P1 | ADR-0011 Error Boundaries | `docs/adr/ADR-0011-error-boundaries.md` | planned | Decide error taxonomy. | Needed for robust diagnostics. | Developers. |
| P1 | ADR-0012 Miova Mutation Boundaries | `docs/adr/ADR-0012-miova-mutation-boundaries.md` | planned | Decide how Miova interacts with FORML. | Critical for mutation testing. | Developers. |

---

# 13. Roadmap documentation

| Priority | Document | Location | Status | Purpose | Why it exists | Audience |
|---:|---|---|---|---|---|---|
| P2 | Implementation Roadmap | `docs/roadmap/implementation-roadmap.md` | planned | Track implementation milestones. | Separates code roadmap from documentation roadmap. | Maintainer. |
| P2 | Documentation Roadmap | `docs/roadmap/documentation-roadmap.md` | planned | Track documentation progress. | Useful after this root roadmap becomes too large. | Maintainer. |
| P2 | Open Questions | `docs/roadmap/open-questions.md` | planned | Track unresolved architecture questions. | Prevents hidden decisions. | Maintainer, contributors. |

---

# Recommended rewrite order

## Batch 1 — Root P0 baseline

```text
docs/index.md
docs/docs-roadmap.md
docs/architecture/overview.md
docs/architecture/status-matrix.md
```

Goal: establish identity, architecture, status, and documentation plan.

## Batch 2 — End-to-end architecture

```text
docs/architecture/pipeline-views.md
docs/architecture/runtime-flow.md
docs/compiler/pipeline.md
docs/compiler/backend-boundary.md
```

Goal: define the full FORML runtime path.

## Batch 3 — Logical pipeline P0

```text
docs/compiler/ir1-layer.md
docs/compiler/ir2-layer.md
docs/compiler/assertion-aggregation.md
docs/compiler/lowering-minimization.md
docs/ir/ir1-nnf.md
docs/ir/ir2-normal-forms.md
docs/ir/aggregated-assertion-set.md
docs/ir/backend-query.md
```

Goal: stabilize the logical verification pipeline.

## Batch 4 — ModelBridge P0

```text
docs/model-bridge/overview.md
docs/model-bridge/model-schema.md
docs/model-bridge/model-constraints.md
docs/contracts/model-to-schema.md
docs/contracts/schema-to-semantic.md
docs/contracts/model-constraints.md
```

Goal: connect models to semantic validation and backend constraints.

## Batch 5 — Contracts P0

```text
docs/contracts/compiler-pipeline.md
docs/contracts/source-to-cst.md
docs/contracts/cst-to-ast.md
docs/contracts/ast-contract.md
docs/contracts/ast-to-semantic.md
docs/contracts/semantic-to-ir1.md
docs/contracts/ir1-to-ir2.md
docs/contracts/assertion-aggregation.md
docs/contracts/lowering-minimization.md
docs/contracts/ir-to-backend.md
docs/contracts/errors.md
docs/contracts/type-normalization.md
docs/contracts/mutation-boundaries.md
```

Goal: make each architecture boundary testable.

## Batch 6 — Miova and testing P0

```text
docs/miova/overview.md
docs/miova/artifact-boundaries.md
docs/miova/mutation-campaigns.md
docs/miova/contract-testing.md
docs/testing/strategy.md
docs/testing/golden-samples.md
docs/testing/end-to-end-tests.md
docs/testing/miova-campaigns.md
```

Goal: turn architecture into executable validation strategy.

## Batch 7 — Language and user docs

```text
docs/language/overview.md
docs/language/grammar.md
docs/language/vocabulary.md
docs/language/syntax.md
docs/language/properties.md
docs/language/scopes.md
docs/language/assertions.md
docs/language/examples.md
```

Goal: make FORML usable and understandable from the outside.

---

# Documentation rule

Every document should include a small status header:

```markdown
> Status: implemented / stabilizing / planned / research-direction  
> Scope: ...  
> Implementation state: ...
```

Every architecture document should distinguish:

```text
Current implementation
Target architecture
Open questions
```

Every contract document should distinguish:

```text
Input artifact
Output artifact
Guarantees
Failure modes
Invariants
Test strategy
Miova mutation relevance
```

This prevents the documentation from becoming either too vague or too implementation-specific.
