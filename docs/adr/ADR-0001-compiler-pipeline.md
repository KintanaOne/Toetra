# ADR-0001 — Use a Staged Compiler Pipeline

> Status: Accepted  
> Date: 2026-06  
> Scope: Compiler architecture

## Context

FORML must transform a `.forml` specification into a verification artifact that can eventually be executed by a backend such as Z3.

A direct translation from raw source code to backend queries would be fragile. It would mix parsing, syntax construction, semantic validation, logical normalization, model awareness, backend concerns, and diagnostics in a single layer.

## Decision

FORML uses a staged compiler pipeline.

The target pipeline is:

```text
.forml source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1 / NNF
→ IR2 / CNF-DNF
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
→ VerificationResult
```

Each stage has its own responsibilities, inputs, outputs, validation rules, and error boundaries.

## Rationale

A staged pipeline makes FORML easier to reason about, test, debug, mutate, and extend.

It also allows each transformation to be documented as a contract:

```text
Input artifact
Preconditions
Transformation
Output artifact
Postconditions
Expected failures
```

## Consequences

### Positive

- The architecture is explicit and inspectable.
- Each layer can be tested independently.
- Miova can mutate artifacts at precise boundaries.
- Future backend support can be added without rewriting the DSL compiler.
- Diagnostics can point to the failing layer.

### Negative

- The architecture is more complex than a direct interpreter.
- More intermediate artifacts must be maintained.
- Documentation and contracts become necessary to avoid ambiguity.

## Alternatives considered

### Direct DSL-to-Z3 translation

Rejected because it would couple user syntax, semantic rules, model metadata, and backend encoding too early.

### Single AST with all responsibilities

Rejected because AST would become overloaded with syntax, semantics, and backend information.

## Impact on FORML

The staged compiler pipeline is the architectural backbone of FORML.

All major documentation sections should align with this staged model.
