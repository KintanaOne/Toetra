# Compiler Pipeline Contract

> Status: P0 / Stabilizing  
> Scope: End-to-end compiler artifact progression  
> Implementation: Implemented until IR1, planned beyond IR1  
> Audience: compiler maintainers, architecture maintainers, Miova campaign authors

## Purpose

The compiler pipeline contract defines the official progression of FORML compiler artifacts.

It answers the question:

```text
Which artifacts are allowed to exist between compiler layers?
```

This contract prevents downstream layers from relying on parser internals, partial AST assumptions, or backend-specific objects too early.

---

## Official Artifact Chain

```text
SourceText
    ↓
CST
    ↓
AST / ProgramNode
    ↓
SemanticValidatedAST
    ↓
IR1 / VerificationTask
    ↓
IR2 / NormalFormIR
    ↓
AggregatedAssertionSet
    ↓
LoweredQuery
    ↓
BackendQuery
```

---

## Current Implementation

| Artifact | Status | Notes |
|---|---|---|
| SourceText | Implemented | Raw `.forml` string. |
| CST | Implemented | Produced by the Lark parser. |
| AST | Implemented / stabilizing | Built as dataclass-based FORML nodes. |
| SemanticValidatedAST | Implemented / stabilizing | Currently represented by AST enriched with semantic annotations. |
| IR1 | Implemented / stabilizing | `VerificationTask`, `ScopeIR`, `QueryIR`, logical nodes. |
| IR1-NNF | Planned / critical | De Morgan and NNF belong here once the pass exists. |
| IR2 | Planned / critical | CNF/DNF and normal-form selection. |
| AggregatedAssertionSet | Planned / critical | DSL assertions + semantic/model constraints. |
| LoweredQuery | Planned / critical | Simplified backend-preparable query. |
| BackendQuery | Planned / critical | Backend-specific executable artifact. |

---

## Global Guarantees

The compiler pipeline must guarantee:

- each layer consumes only the artifact type declared by the previous layer;
- each layer either produces a valid next artifact or fails explicitly;
- no backend-specific object leaks before the backend boundary;
- semantic resolution is preserved from semantic validation to IR;
- logical transformations declare whether they preserve equivalence or equisatisfiability;
- each layer has a clear mutation boundary for Miova.

---

## Non-Goals

The compiler pipeline contract does not define:

- the full syntax of the DSL;
- the internal implementation of each transformation;
- backend-specific solver encoding details;
- runtime monitoring behavior;
- user-facing documentation examples.

Those concerns are documented in dedicated sections.

---

## Expected Failure Boundaries

| Failure | Expected Boundary |
|---|---|
| Invalid syntax | Source → CST |
| Unsupported grammar construct | Source → CST or CST → AST |
| Missing AST field | CST → AST |
| Unbound variable | AST → Semantic |
| Incompatible property/scope | AST → Semantic |
| Invalid logical transform | Semantic → IR1 or IR1 → IR2 |
| Unsupported model schema | Model → Schema or Schema → Semantic |
| Unsupported backend feature | IR → Backend |

---

## Miova Contract Testing

Miova should be able to test the pipeline by applying mutations at each artifact layer.

Examples:

| Layer | Mutation Example | Expected Outcome |
|---|---|---|
| Source | corrupt keyword, operator, bracket | parser rejection |
| AST | remove scope, backend, assertion | builder/semantic rejection |
| Semantic | remove binding metadata | IR translation rejection |
| IR1 | insert invalid negation shape | IR2 rejection |
| IR2 | corrupt CNF/DNF structure | aggregation/lowering rejection |
| ModelSchema | remove feature dtype | schema-semantic rejection |
