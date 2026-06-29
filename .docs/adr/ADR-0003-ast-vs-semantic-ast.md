# ADR-0003 — Separate Raw AST from SemanticValidatedAST

> Status: Accepted  
> Date: 2026-06  
> Scope: AST and semantic validation

## Context

The AST represents the structured syntax of a `.forml` specification.

However, the AST alone does not prove that:

- variables are bound,
- implicit entities are resolved,
- scopes are compatible with property types,
- problem/function pairs are valid,
- attributes refer to meaningful model-side features,
- logical expressions are semantically valid.

## Decision

FORML separates:

```text
AST
```

from:

```text
SemanticValidatedAST
```

The AST is produced by the builder.

The SemanticValidatedAST is produced after semantic validation and contains resolved semantic metadata through semantic annotations and contexts.

## Rationale

Syntax construction and semantic validation are different responsibilities.

The AST answers:

```text
What did the user write?
```

The SemanticValidatedAST answers:

```text
What does it mean in a FORML verification context?
```

## Consequences

### Positive

- Builder remains syntax-oriented.
- Semantic validation can evolve independently.
- IR generation can rely on resolved entities and contexts.
- Errors are easier to classify.
- Miova can distinguish syntax-preserving mutations from semantic mutations.

### Negative

- Some nodes need semantic metadata after construction.
- Care must be taken to avoid treating raw AST as semantically safe.
- Naming and typing must make the distinction explicit.

## Alternatives considered

### Attach semantics during parsing

Rejected because parsing should not know semantic scope rules.

### Generate IR directly from AST

Rejected because IR needs resolved semantic information, not only syntax.

## Impact on FORML

IR generation should consume the SemanticValidatedAST, not the raw AST.

Any direct AST-to-backend path should be considered invalid.
