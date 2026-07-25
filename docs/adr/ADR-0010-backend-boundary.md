# ADR-0010 — Use Z3 as the Minimal V1 Backend Boundary

> Status: Accepted  
> Date: 2026-06  
> Scope: Backend strategy

## Context

Toetra is designed to support multiple verification backends in the long term.

Potential future backends may include ERAN, abstract interpretation tools, model checkers, runtime monitors, or other solver systems.

However, supporting multiple backends too early would increase complexity before the end-to-end path is stable.

## Decision

Z3 is the minimal backend for Toetra V1.

The V1 backend strategy is:

```text
LoweredQuery
→ Z3 BackendQuery
→ Z3 Solver Execution
→ VerificationResult
```

ERAN and other backends are post-V1 extensions.

## Rationale

Z3 is sufficient to validate the first end-to-end Toetra architecture:

```text
DSL
→ semantic validation
→ IR
→ aggregation
→ lowering
→ backend query
→ solver result
```

A Z3-first strategy avoids premature multi-backend overengineering while preserving the backend boundary for future extension.

## Consequences

### Positive

- V1 scope remains realistic.
- Backend abstraction can be designed without implementing all backends.
- The first end-to-end path can be validated sooner.
- Future backends can be added after the architecture is proven.

### Negative

- Some ML verification capabilities may be limited in V1.
- ERAN-like neural verification is deferred.
- Backend capability scoring is not a V1 requirement.

## Alternatives considered

### Multi-backend V1

Rejected because it would delay a functional end-to-end system.

### No backend boundary until Z3 works

Rejected because backend concerns must not leak into IR and aggregation layers.

## Impact on Toetra

All docs should treat Z3 as the only V1 backend.

ERAN and other backends should be documented as future/post-V1 extensions only.
