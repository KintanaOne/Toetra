# ADR-0011 — Preserve Error Boundaries Between Layers

> Status: Stabilizing  
> Date: 2026-06  
> Scope: Diagnostics and failure classification

## Context

Toetra has many possible failure points:

- syntax errors,
- builder errors,
- invalid AST structure,
- semantic binding errors,
- property/scope incompatibility,
- type mismatches,
- unsupported model formats,
- unsupported model frameworks,
- invalid IR transformations,
- backend lowering failures,
- solver failures.

If all errors are wrapped into a generic error type, diagnostics become unclear and tests become weaker.

## Decision

Toetra preserves error boundaries between layers.

Each layer should expose its own error category:

```text
ParserError
BuilderError
ASTContractError
SemanticError
ModelError
IRError
AggregationError
LoweringError
BackendError
RuntimeError
```

## Rationale

Precise error boundaries make Toetra easier to debug and easier to test.

They are also necessary for Miova expected-failure classification.

## Consequences

### Positive

- Clearer diagnostics.
- Better test.
- Expected failures can be asserted by layer.
- Mutation campaigns can distinguish accepted, rejected, skipped, and failed artifacts.

### Negative

- Requires a consistent error hierarchy.
- Some existing broad exception wrapping may need refactoring.
- Documentation must define expected failures per contract.

## Alternatives considered

### Wrap everything into ParserError

Rejected because it destroys semantic and backend error information.

### Use only Python built-in exceptions

Rejected because Toetra needs domain-specific diagnostics.

## Impact on Toetra

Error boundaries are part of the compiler contract.

They must be reflected in documentation, tests, and Miova campaigns.
