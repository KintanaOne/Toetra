# Artifact Boundaries

> Status: planned / critical  
> Scope: FORML artifacts exposed to Miova  
> Audience: compiler maintainers, mutation authors, testing engineers

## Purpose

This document defines the artifact boundaries where Miova may interact with FORML.

A boundary is a stable transformation point between two layers. Each boundary has:

- an input artifact;
- an output artifact;
- a contract;
- expected invariants;
- valid mutation strategies;
- expected failure behavior.

## Why Boundaries Matter

FORML is not a single transformation. It is a sequence of progressively stronger representations.

```text
Source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1
→ IR2
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
```

Miova should not mutate arbitrary internal objects without architectural meaning.

It should mutate artifacts at explicit boundaries.

## Boundary Map

| Boundary | Input | Output | Main Contract |
|---|---|---|---|
| Source → CST | `.forml` string | CST | Syntax must be accepted or rejected deterministically. |
| CST → AST | CST | AST | Syntax tree must become a strict typed AST. |
| AST → Semantic | AST | SemanticValidatedAST | Variables, scopes, bindings, and property compatibility must be resolved. |
| Semantic → IR1 | SemanticValidatedAST | IR1 | Semantic meaning must be preserved in logical form. |
| IR1 → IR2 | IR1 | IR2 | NNF logic must become selected CNF/DNF or canonical forms. |
| Model → Schema | serialized model / dataset | ModelSchema | Model metadata must be normalized. |
| Schema → Semantic | ModelSchema + AST | schema-aware semantic state | DSL references must match model features and task. |
| ModelSchema → ModelConstraints | ModelSchema | ModelConstraintIR | Model metadata must become constraint-ready. |
| IR2 + Constraints → Aggregation | IR2 + semantic/model constraints | AggregatedAssertionSet | Assertions must compose without semantic loss. |
| Aggregation → Lowering | AggregatedAssertionSet | LoweredQuery | Simplification must preserve verification intent. |
| Lowering → Backend | LoweredQuery | BackendQuery | Backend-specific encoding must satisfy backend contract. |

## Artifact Kinds

Miova should use stable artifact kinds to identify mutation targets.

| Kind | Meaning |
|---|---|
| `forml.source` | Raw FORML source text. |
| `forml.cst` | Parser-produced CST. |
| `forml.ast` | Builder-produced AST. |
| `forml.semantic_ast` | AST enriched by semantic validation. |
| `forml.ir1` | First logical IR, including NNF-oriented normalization. |
| `forml.ir2` | Clause or normal-form IR. |
| `forml.model_schema` | Normalized model schema from ModelBridge. |
| `forml.model_constraints` | Future model-derived constraints. |
| `forml.aggregated_assertions` | Combined verification problem. |
| `forml.lowered_query` | Simplified backend-preparation query. |
| `forml.backend_query` | Backend-specific executable query artifact. |

## Mutation Safety

A mutation is safe when its expected result is explicit.

A mutation can be intended to:

- preserve validity;
- preserve syntax but break semantics;
- preserve semantics but change structure;
- weaken a property;
- strengthen a property;
- corrupt a layer intentionally;
- test a specific diagnostic path.

No mutation should be considered valid only because it does not crash.

## Boundary Invariant Pattern

Each boundary should eventually define invariants using this pattern:

```text
Before invariant:
    The input artifact is valid for its declared layer.

Transition invariant:
    The transformation preserves or intentionally changes the declared property.

After invariant:
    The output artifact satisfies the target layer contract.
```

## Example Boundary: AST → Semantic

| Aspect | Description |
|---|---|
| Input artifact | AST |
| Output artifact | SemanticValidatedAST |
| Valid mutation | Replace implicit attribute access with explicit entity access. |
| Invalid mutation | Reference an unknown entity. |
| Expected failure | `UnboundVariableError` or semantic validation rejection. |
| Invariant | All attribute nodes used in comparisons must be semantically resolved. |

## Example Boundary: IR1 → IR2

| Aspect | Description |
|---|---|
| Input artifact | IR1 logical tree in NNF-oriented form. |
| Output artifact | IR2 normal-form representation. |
| Valid mutation | Reorder operands in commutative nodes. |
| Invalid mutation | Drop one side of a conjunction without marking weakening. |
| Expected failure | Contract rejection or preservation violation. |
| Invariant | Transformation must preserve semantic equivalence or explicitly track equisatisfiability. |

## Boundary Ownership

Each boundary should have one owning module and one owning test suite.

| Boundary | Owning area |
|---|---|
| Source → CST | Parser |
| CST → AST | Builder |
| AST → Semantic | Semantic validator |
| Semantic → IR1 | IR translator |
| IR1 → IR2 | Logical normalization |
| Model → Schema | ModelBridge |
| Aggregation → Lowering | Logical verification pipeline |
| Lowering → Backend | Backend compiler |

## P0 Requirement

At P0, the most important mutation boundaries are:

1. Source → CST;
2. CST → AST;
3. AST → Semantic;
4. Semantic → IR1;
5. Model → Schema;
6. Schema → Semantic;
7. IR1 → IR2;
8. Assertion aggregation;
9. Lowering;
10. Backend query generation.
