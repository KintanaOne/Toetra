# ADR-0012 — Use Miova for Mutation Boundaries and Contract Validation

> Status: Accepted  
> Date: 2026-06  
> Scope: Testing and robustness validation

## Context

Toetra is a layered compiler and verification pipeline.

Testing only hand-written examples is not enough to validate the robustness of such a system.

Toetra needs to know how each layer behaves when artifacts are mutated:

- source text mutations,
- CST mutations,
- AST mutations,
- semantic AST mutations,
- IR mutations,
- ModelSchema mutations,
- aggregated assertion mutations,
- backend query mutations.

## Decision

Toetra uses Miova as an external mutation and contract validation framework.

Miova is not part of the normal verification runtime path.

Miova is used to challenge Toetra artifacts, validate contracts, test invariants, and classify expected failures.

## Rationale

Miova provides a structured way to test Toetra as a system of artifacts and transformations.

It complements:

- unit tests,
- property-based tests,
- golden samples,
- end-to-end tests,
- intelligent fuzzing.

## Consequences

### Positive

- Toetra can be tested beyond happy paths.
- Mutation boundaries are explicit.
- Contract violations can be discovered earlier.
- Expected failures become part of the test model.
- Future LLM-assisted property generation can rely on stronger artifact contracts.

### Negative

- Mutation campaigns require careful design.
- Some mutations may create invalid artifacts intentionally.
- Test output must distinguish expected rejection from real system failure.

## Alternatives considered

### Use Hypothesis only

Rejected because Hypothesis generates examples well, but Miova adds artifact-level mutation contracts, invariants, lineage, and expected-failure semantics.

### Use fuzzing only at source level

Rejected because many bugs appear only after CST, AST, semantic, or IR transformations.

## Impact on Toetra

Miova is a strategic testing and robustness layer for Toetra.

Every major artifact boundary should eventually have Miova mutations, invariants, and expected-failure rules.
