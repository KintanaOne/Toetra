# AST to Semantic Contract

> Status: P0 / Implemented / Stabilizing  
> Scope: AST to SemanticValidatedAST  
> Implementation: LHS validation, binding validation, logic validation, compatibility checks  
> Audience: semantic maintainers, compiler authors, Miova campaign authors

## Purpose

The AST to Semantic contract defines how raw AST syntax becomes semantically validated FORML.

It answers the question:

```text
What does this FORML property mean in its evaluation context?
```

This is the boundary where scope, binding, symbols and property compatibility are resolved.

---

## Input

```text
ProgramNode / PropertyNode
```

Preconditions:

- AST was produced by the builder;
- nodes are structurally present;
- variables may still be unresolved;
- feature references may still be implicit.

---

## Output

```text
SemanticValidatedAST
```

Current representation:

```text
AST + SemanticAnnotations
```

The semantic layer enriches properties and attributes with:

- semantic context;
- symbol table;
- resolved entity;
- resolved path;
- resolved symbol;
- logical root cache;
- scope metadata.

---

## Semantic Pipeline

```text
PropertyNode
    ↓
LHS validation
    ↓
SemanticContext
    ↓
Binding validation
    ↓
resolved attributes
    ↓
Logic validation
    ↓
property/scope compatibility
    ↓
SemanticValidatedAST
```

---

## Main Responsibilities

| Step | Responsibility |
|---|---|
| LHS validation | Determine semantic scope and variable roles. |
| Symbol registration | Register anchor, perturbation, symbolic variables. |
| Binding validation | Resolve explicit and implicit attribute references. |
| Logic validation | Validate logical node structure and problem predicates. |
| Compatibility validation | Ensure property type supports the semantic scope. |

---

## Scope Semantics

| Scope | Variables | Default Entity | Meaning |
|---|---|---|---|
| `check_at` | `x` | `x` | Pointwise evaluation. |
| `at` | `x`, `x'` | `x'` | Local perturbation evaluation. |
| `pairwise` | `x`, `x'` | `x'` | Pairwise relation between anchor and perturbation. |
| quantifier | `_x` | `_x` | Symbolic universal/existential evaluation. |

---

## Guarantees

If semantic validation succeeds:

- all attributes used in comparisons are resolved;
- implicit feature access has a resolved entity;
- semantic context exists for each property;
- property/scope compatibility has been checked;
- problem/function compatibility has been checked;
- IR translation may consume semantic annotations.

---

## Non-Goals

The semantic layer must not:

- produce IR directly;
- perform NNF/CNF/DNF rewriting;
- encode model internals as solver constraints;
- choose backend strategy;
- execute verification.

---

## Stabilization Notes

The semantic contract should stabilize:

- enum normalization at semantic boundaries;
- problem/function compatibility handling;
- property/scope compatibility handling;
- quantifier normalization;
- semantic error boundaries;
- distinction between parser errors and semantic errors;
- feature validation against ModelSchema once schema integration is available.

---

## Miova Hooks

Miova may challenge semantic validation by:

- removing semantic context;
- corrupting variable roles;
- replacing a scope with an incompatible property;
- making implicit attributes ambiguous;
- introducing unresolved entities;
- corrupting problem/function combinations.

Expected outcome:

```text
Invalid semantic mutation → semantic rejection
Valid semantic mutation   → IR translation may continue
```
