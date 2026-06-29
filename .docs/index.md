# FORML

> Status: P0 documentation baseline  
> Scope: Project identity, end-to-end vision, and documentation entry point  
> Implementation state: Partially implemented, architecturally expanding

FORML is a behavioral specification and verification framework for machine learning systems.

It provides a domain-specific language and compilation pipeline for expressing, validating, normalizing, and eventually lowering behavioral properties of ML models into backend-specific verification queries.

FORML is not only a DSL. It is designed as an end-to-end verification architecture connecting:

- user-defined behavioral intent,
- structured compiler artifacts,
- semantic validation,
- logical intermediate representations,
- model metadata and model-derived constraints,
- backend-oriented query generation,
- and future verification runtimes.

## Why FORML exists

Machine learning systems are usually evaluated through metrics, datasets, test sets, and monitoring dashboards. These tools are useful, but they rarely express behavioral requirements as explicit, reusable, verifiable properties.

FORML is built around a different question:

> What behavioral properties should a model satisfy, and how can those properties be represented, validated, transformed, and checked across a verification pipeline?

Examples of FORML-style concerns include:

- robustness around a point or within a neighborhood,
- monotonicity between two model inputs,
- bounds over model behavior,
- stability under controlled perturbations,
- fairness-like pairwise comparisons,
- and logical combinations of domain constraints and model behavior.

The long-term goal is to make ML behavior specification as explicit as software contracts, test properties, or formal verification assertions.

## Core idea

A `.forml` file describes properties that should hold for a target ML model.

FORML progressively transforms this source specification into increasingly formal artifacts:

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
Lowering / Minimization
    ↓
Backend Query
    ↓
Verification Result
```

The current implementation focuses on the compiler front-end, semantic validation, IR1 generation, and the ModelBridge foundation. Later layers are part of the target end-to-end architecture and are documented explicitly as planned or research-direction components.

## Main subsystems

### DSL Compiler Pipeline

The compiler pipeline transforms `.forml` specifications into structured and validated representations.

Its responsibility is to move from raw text to typed, validated, backend-independent logical artifacts.

```text
Source → CST → AST → SemanticValidatedAST → IR1
```

The current compiler already includes parsing, AST construction, semantic context generation, binding validation, logical validation, and IR1 translation.

### Logical Verification Pipeline

The logical verification pipeline starts after semantic validation.

Its role is to normalize, transform, aggregate, simplify, and prepare verification logic before backend-specific lowering.

```text
SemanticValidatedAST
    ↓
IR1 / NNF
    ↓
IR2 / CNF-DNF
    ↓
Assertion Aggregation
    ↓
Lowering / Minimization
    ↓
Backend Query
```

IR1 is responsible for the first backend-independent logical representation and includes De Morgan / NNF-oriented normalization. IR2 is planned as the layer responsible for clause-oriented or case-oriented forms such as CNF and DNF.

### ModelBridge

ModelBridge connects FORML specifications to actual ML model artifacts.

It is responsible for:

- loading serialized models,
- detecting their framework,
- introspecting model and dataset metadata,
- producing a normalized `ModelSchema`,
- supporting semantic validation against model features,
- and later generating model-side constraints for backend lowering.

ModelBridge is not just a metadata helper. It is the bridge between ML runtime objects and formal verification artifacts.

### Backend Boundary

FORML is designed to be backend-agnostic.

A backend may be a solver, verifier, symbolic engine, runtime checker, or model-specific verification system.

The backend boundary is where FORML-specific logical artifacts become backend-specific queries.

Examples of future backends include:

- Z3,
- ERAN,
- zonotope or box abstractions,
- runtime monitors,
- and other verification engines.

### Miova Integration

Miova is not part of the normal FORML verification path.

Miova is an external mutation and exploration framework used to challenge FORML artifacts across compiler and verification boundaries.

It helps answer questions such as:

- Does a compiler layer reject invalid artifacts correctly?
- Does a mutation preserve or violate a contract as expected?
- Which transformations are robust to controlled perturbations?
- Where are the limits of the DSL, semantic layer, IR, or backend boundary?

Miova is therefore a testing, validation, and exploration layer around FORML, not a replacement for FORML itself.

## Design principles

### Progressive formalization

Each layer introduces stronger structure and stronger guarantees.

Raw DSL text becomes CST, CST becomes AST, AST becomes semantically validated AST, semantic artifacts become IR, IR becomes normalized logic, and normalized logic becomes backend-ready queries.

### Explicit artifacts

FORML treats each pipeline stage as a meaningful artifact.

This makes transformation boundaries explicit and testable.

### Contract-oriented compilation

Each transformation should have a clear contract:

- input artifact,
- output artifact,
- guarantees,
- failure modes,
- invariants,
- and traceability rules.

### Semantic preservation

Transformations should preserve the meaning of user intent unless a pass explicitly documents that it preserves only equisatisfiability or introduces a controlled approximation.

### Backend-agnostic reasoning

The DSL and early IR layers should not depend on a single backend.

Backend-specific choices belong near the backend boundary, not in the parser, AST, or semantic layer.

### Model-aware verification

A FORML property is not fully meaningful until it can be checked against the model schema, task, target, features, and model-derived constraints.

ModelBridge is therefore central to the end-to-end architecture.

## Current implementation snapshot

| Subsystem | Status | Notes |
|---|---|---|
| DSL grammar | Implemented / stabilizing | Lark grammar exists; syntax and vocabulary normalization still need cleanup. |
| Parser | Implemented | Produces CST from `.forml` source. |
| AST builder | Implemented / stabilizing | Converts CST into structured AST nodes. |
| Semantic validation | Implemented / stabilizing | Builds semantic context, resolves bindings, validates logic and property-scope compatibility. |
| IR1 | Implemented / stabilizing | Produces backend-independent verification tasks and logical IR. |
| IR1 NNF / De Morgan | Implemented / stabilizing | Treated as part of the IR1 normalization responsibility. |
| IR2 CNF / DNF | Planned / critical | Required before advanced backend preparation. |
| ModelBridge | Partially implemented | Loading, framework detection, introspection, and `ModelSchema` foundation exist. |
| Assertion aggregation | Planned / critical | Required to combine DSL assertions, semantic constraints, and model constraints. |
| Lowering / minimization | Planned / critical | Required before backend-specific query generation. |
| Backend query generation | Planned / critical | Z3 is the first intended target. |
| Runtime verification | Planned | Depends on backend boundary and query execution. |
| Miova integration | Planned / critical | Used for mutation campaigns and contract testing. |

## Documentation map

The documentation is organized around several concerns:

- **Architecture**: system views, runtime flow, status matrix.
- **Language**: grammar, vocabulary, syntax, properties, assertions.
- **Compiler**: parser, builder, AST, semantic layer, IR1, IR2, aggregation, lowering.
- **ModelBridge**: model loading, detection, introspection, schema, constraints.
- **Intermediate Representations**: IR1, IR2, aggregated assertions, backend queries.
- **Contracts**: layer boundaries and invariants.
- **Backends**: capabilities, orchestration, Z3 and future backend targets.
- **Miova Integration**: artifact mutation, contracts, invariants, expected failures.
- **Testing**: unit tests, golden samples, end-to-end tests, mutation campaigns.
- **ADRs**: design decisions and architectural trade-offs.

## Next reading

Start with:

1. [Documentation Roadmap](docs-roadmap.md)
2. [Architecture Overview](architecture/overview.md)
3. [Status Matrix](architecture/status-matrix.md)

These three documents define the structure used by the rest of the documentation.
