# ADR-0005 — Use Semantic Annotations as Runtime Semantic Cache

> Status: Accepted  
> Date: 2026-06  
> Scope: Semantic validation

## Context

Semantic validation produces information that downstream layers need:

- resolved entity,
- resolved path,
- resolved symbol,
- semantic context,
- symbol table,
- scope type,
- validated logical root.

This information is not part of the raw user syntax, but it is essential for IR generation and backend preparation.

## Decision

Toetra uses semantic annotations as a runtime semantic cache attached to semantic-capable nodes.

Semantic annotations are not an IR layer and not the source of truth for syntax.

They are a cache of resolved semantic metadata.

## Rationale

Semantic annotations allow the semantic validator to enrich AST nodes without immediately converting them to IR.

This provides a clear bridge between:

```text
syntax-oriented AST
```

and:

```text
backend-independent IR
```

## Consequences

### Positive

- Resolved bindings are available to IR translation.
- Semantic validation can be inspected and debugged.
- Future passes can reuse semantic metadata.
- Attribute resolution can preserve both raw and resolved forms.

### Negative

- Node classes must consistently support semantic annotations.
- Mutability must be handled carefully.
- The boundary between annotations and IR must remain clear.

## Alternatives considered

### Create a completely separate semantic tree

Deferred. It may become useful later, but semantic annotations are simpler for the current V1.

### Store semantic state only in validator-local structures

Rejected because downstream layers need access to resolution results.

## Impact on Toetra

Semantic annotations are part of the SemanticValidatedAST contract.

IR translation must prefer resolved semantic information over raw syntax where applicable.
