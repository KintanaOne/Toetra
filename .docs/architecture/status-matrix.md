# Architecture Status Matrix

> Status: P0 documentation baseline  
> Scope: Implementation status across FORML subsystems  
> Purpose: Distinguish implemented, stabilizing, planned, and research-direction components

This document tracks the state of the FORML architecture.

FORML intentionally documents both current implementation and target architecture. This matrix prevents ambiguity by making the status of each subsystem explicit.

## Status legend

| Status | Meaning |
|---|---|
| `implemented` | Exists in code and is usable. |
| `stabilizing` | Exists but needs cleanup, stronger contracts, tests, naming normalization, or API refinement. |
| `partially implemented` | Some components exist, but the subsystem is not complete. |
| `planned / critical` | Not implemented yet but required for end-to-end FORML verification. |
| `planned` | Intended future layer, but not the immediate blocker. |
| `research-direction` | Long-term idea, not a current implementation claim. |
| `external` | Handled by another project or external system. |

---

# Global subsystem matrix

| Subsystem | Status | Implementation evidence | Target role | Priority |
|---|---|---|---|---:|
| DSL grammar | implemented / stabilizing | Lark grammar and generated grammar exist. | Stable source language for `.forml` specifications. | P1 |
| Parser | implemented | Parser produces CST from `.forml` source. | Strict source-to-CST boundary. | P0 |
| AST builder | implemented / stabilizing | Builder modules construct `ProgramNode`, `PropertyNode`, expressions, assertions, backend nodes. | Strict CST-to-AST contract. | P0 |
| AST model | implemented / stabilizing | AST dataclasses exist, but semantic attachment strategy needs cleanup. | Stable typed syntax tree. | P0 |
| Semantic context | implemented / stabilizing | `SemanticContext`, `SemanticScope`, `SymbolTable` exist. | Meaning context for scopes, variables, domains, neighborhoods. | P0 |
| Binding validation | implemented / stabilizing | Explicit and implicit attribute resolution exists. | Resolve RHS references to semantic entities. | P0 |
| Logic validation | implemented / stabilizing | Logical nodes and problem validation exist. | Validate logical structure and semantic compatibility. | P0 |
| Property/scope compatibility | implemented / stabilizing | Compatibility tables exist. | Prevent invalid property/scope combinations. | P0 |
| Semantic annotations | implemented / stabilizing | `SemanticAnnotations` exists. | Cache semantic resolution for IR lowering. | P0 |
| IR1 | implemented / stabilizing | `VerificationTask`, `ScopeIR`, `QueryIR`, `LogicalIR` nodes exist. | First backend-independent logical representation. | P0 |
| IR1 NNF / De Morgan | implemented / stabilizing | Current architecture intent places De Morgan and NNF in IR1. | Normalize negations and logical structure. | P0 |
| IR2 CNF / DNF | planned / critical | Not implemented yet. | Clause/case-oriented normal forms for backend preparation. | P0 |
| Assertion aggregation | planned / critical | Not implemented yet. | Combine DSL, semantic, model, and backend constraints. | P0 |
| Lowering / minimization | planned / critical | Not implemented yet. | Simplify and prepare aggregated assertions for backend query generation. | P0 |
| Backend query | planned / critical | Not implemented yet. | First backend-specific executable/query artifact. | P0 |
| Backend orchestration | planned | Architecture view exists conceptually. | Select backend strategy based on capabilities and constraints. | P1 |
| Z3 backend | planned / critical | Not implemented in current snapshot. | First likely solver backend. | P1 |
| Runtime verification | planned | Conceptual target. | Execute backend queries and produce results. | P2 |
| Runtime monitoring | research-direction | Conceptual target. | Observe behavior after deployment or runtime execution. | P2 |
| Model loading | implemented / stabilizing | Loader factory and pkl/joblib/json loaders exist. | Load model artifacts. | P0 |
| Model detection | implemented / stabilizing | Detector supports sklearn/XGBoost foundations. | Identify model framework. | P0 |
| Model introspection | implemented / stabilizing | Sklearn and XGBoost introspectors exist. | Extract model metadata. | P0 |
| ModelSchema | implemented / stabilizing | `ModelSchema` and `FeatureSchema` exist. | Bridge model metadata to semantic validation and backend lowering. | P0 |
| Model constraints | planned / critical | Not implemented yet. | Generate constraints from ModelSchema and model metadata. | P0 |
| Schema-aware semantic validation | planned / critical | Not implemented yet. | Validate DSL feature references against model schema. | P0 |
| Miova integration | external / planned integration | Miova exists as independent mutation framework. | Challenge FORML artifacts with mutation campaigns. | P0 |
| Golden samples | planned / critical | Not formalized yet. | Freeze expected outputs across the pipeline. | P0 |
| Contract tests | planned / critical | Not formalized yet. | Make layer contracts executable. | P0 |

---

# Compiler pipeline status

```text
.forml source
    ↓ implemented
CST
    ↓ implemented / stabilizing
AST
    ↓ implemented / stabilizing
SemanticValidatedAST
    ↓ implemented / stabilizing
IR1 / NNF
    ↓ planned / critical
IR2 / CNF-DNF
    ↓ planned / critical
Aggregated Assertion Set
    ↓ planned / critical
Lowering / Minimization
    ↓ planned / critical
Backend Query
```

## Current compiler guarantees

| Layer | Current guarantee | Gap |
|---|---|---|
| Source → CST | Source can be parsed by Lark grammar. | Grammar/token casing and vocabulary alignment need cleanup. |
| CST → AST | CST can be transformed into structured AST nodes. | AST invariants and error boundaries need formal contracts. |
| AST → Semantic | LHS context, binding, and logic validation exist. | Semantic errors are not yet cleanly separated from parser errors in all paths. |
| Semantic → IR1 | IR1 tasks can be generated. | IR should consume resolved semantic annotations consistently. |
| IR1 → IR2 | Not implemented. | CNF/DNF contract required. |
| IR2 → Aggregation | Not implemented. | Aggregated assertion artifact required. |
| Aggregation → Lowering | Not implemented. | Simplification/minimization contract required. |
| Lowering → Backend Query | Not implemented. | Backend-specific boundary required. |

---

# ModelBridge status

```text
model artifact
    ↓ implemented / stabilizing
loader
    ↓ implemented / stabilizing
loaded model
    ↓ implemented / stabilizing
framework detection
    ↓ implemented / stabilizing
introspector
    ↓ implemented / stabilizing
ModelSchema
    ↓ planned / critical
model constraints
    ↓ planned / critical
assertion aggregation
```

## Current ModelBridge guarantees

| Layer | Current guarantee | Gap |
|---|---|---|
| Model path → loader | Loader is selected by file extension. | Loader error taxonomy needs cleanup. |
| Loader → loaded model | Pickle/joblib loading exists. | JSON loader error naming needs stabilization. |
| Loaded model → framework | sklearn and XGBoost-style detection exists. | PyTorch/TensorFlow are enum values but not implemented. |
| Framework → introspector | Factory selects sklearn/XGBoost introspectors. | Unsupported frameworks need explicit diagnostics. |
| Introspector → ModelSchema | Schema can be produced from model/dataset/schema metadata. | Schema-aware semantic validation is not connected yet. |
| ModelSchema → model constraints | Not implemented. | Required for real backend query generation. |

---

# Logical representation status

| Artifact | Status | Role | Required next step |
|---|---|---|---|
| `VerificationTask` | implemented / stabilizing | Top-level IR1 unit. | Ensure it remains backend-independent until backend boundary. |
| `ScopeIR` | implemented / stabilizing | Represents semantic evaluation scope. | Align roles with semantic context naming. |
| `QueryIR` | implemented / stabilizing | Wraps logical expression. | Clarify whether multiple queries aggregate before or after IR2. |
| `LogicalIR` | implemented / stabilizing | Base for boolean reasoning. | Define normalization invariants. |
| `ComparisonIR` | implemented / stabilizing | Atomic predicate. | Use resolved semantic entity/path consistently. |
| `ProblemIR` | implemented / stabilizing | High-level ML semantic predicate. | Define lowering into backend/model constraints. |
| `AndIR` / `OrIR` / `NotIR` / `ImplyIR` | implemented / stabilizing | Boolean structure. | Define NNF and implication-elimination rules. |
| IR2 normal forms | planned / critical | CNF/DNF representation. | Define data model and transformation contract. |
| Aggregated assertions | planned / critical | Combined verification problem. | Define artifact shape. |
| Backend query | planned / critical | Backend-specific execution artifact. | Define Z3 query boundary first. |

---

# Testing status

| Testing layer | Status | Purpose | Priority |
|---|---|---|---:|
| Parser unit tests | existing / stabilizing | Check grammar accepts/rejects samples. | P1 |
| Builder unit tests | existing / stabilizing | Check AST construction. | P1 |
| Semantic unit tests | existing / stabilizing | Check binding, scopes, compatibility. | P0 |
| IR1 tests | stabilizing | Check semantic-to-IR output. | P0 |
| Golden samples | planned / critical | Freeze expected pipeline outputs. | P0 |
| End-to-end tests | planned / critical | Test `.forml + model → backend query/result`. | P0 |
| Contract tests | planned / critical | Validate every layer boundary. | P0 |
| Miova mutation campaigns | planned / critical | Challenge artifacts and expected failures. | P0 |

---

# Documentation status

| Documentation area | Status | Priority | Next action |
|---|---|---:|---|
| Root docs | stabilizing | P0 | Write `index.md`, roadmap, overview, status matrix. |
| Architecture docs | planned / stabilizing | P0 | Rewrite pipeline views and runtime flow. |
| Compiler docs | planned / stabilizing | P0 | Write compiler pipeline and IR docs. |
| ModelBridge docs | planned / stabilizing | P0 | Write overview/schema/constraints docs. |
| Contract docs | planned | P0 | Write boundary contracts. |
| Miova docs | planned | P0 | Write integration and campaign docs. |
| Language docs | planned | P1 | Write syntax and vocabulary docs after contracts. |
| Backends docs | planned | P1 | Start with Z3 boundary. |
| Runtime docs | planned | P2 | Write after backend query execution exists. |
| ADRs | planned | P1 | Write after P0 contracts are drafted. |

---

# Immediate P0 blockers

The following items should be stabilized before claiming a full end-to-end FORML pipeline:

1. IR1 must consistently use semantic annotations instead of raw unresolved AST fields.
2. IR2 CNF/DNF artifact and transformation contract must be defined.
3. Assertion aggregation must be defined as a first-class artifact.
4. ModelSchema must be connected to semantic validation.
5. Model-derived constraints must be defined.
6. Lowering/minimization must define equivalence/equisatisfiability guarantees.
7. Backend query shape must be defined, likely starting with Z3.
8. Error boundaries must distinguish parser, builder, semantic, model, IR, and backend failures.
9. Golden samples must be created for representative properties.
10. Miova mutation boundaries must be mapped to FORML artifacts.

---

# Recommended next documentation batch

After this root batch, the next documentation batch should be:

```text
docs/architecture/pipeline-views.md
docs/architecture/runtime-flow.md
docs/compiler/pipeline.md
docs/compiler/backend-boundary.md
```

This will turn the current roadmap into a concrete end-to-end architecture narrative.
