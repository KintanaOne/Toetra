# Expected Failures

> Status: planned / critical  
> Scope: expected failure classification for mutation-driven testing  
> Audience: maintainers, testing engineers, mutation authors

## Purpose

Expected failures define how FORML should fail when artifacts are invalid.

Miova relies on expected failure classification to distinguish:

- successful rejection;
- incorrect acceptance;
- unexpected crashes;
- wrong-layer diagnostics.

## Why Expected Failures Matter

In a layered compiler and verification pipeline, failure is normal.

Invalid artifacts should fail early, deterministically, and at the correct boundary.

The goal is not to avoid all failures.

The goal is to ensure that failures are meaningful.

## Failure Classification

| Classification | Meaning |
|---|---|
| Expected rejection | Artifact was invalid and rejected by the correct layer. |
| Wrong-layer rejection | Artifact was invalid but rejected too late or by the wrong layer. |
| Unexpected acceptance | Invalid artifact passed a boundary. Critical issue. |
| Unexpected crash | Implementation failed outside expected diagnostic path. |
| Mutation invalid | Mutation was incorrectly defined for the artifact. |
| Contract mismatch | Expected outcome and layer contract disagree. |

## Failure Boundaries

| Layer | Expected Failure Examples |
|---|---|
| Parser | malformed syntax, invalid token sequence, unclosed expression. |
| Builder | missing required CST node, invalid property structure, unsupported assertion node. |
| Semantic | unknown variable, ambiguous implicit feature, incompatible property/scope pair. |
| IR1 | unresolved semantic binding, unsupported logical node, invalid problem mapping. |
| IR2 | invalid normal-form conversion, unsupported CNF/DNF target. |
| ModelBridge | unsupported model format, unsupported framework, missing feature metadata. |
| Schema-Semantic | DSL references unknown feature, task mismatch, dtype incompatibility. |
| Aggregation | contradictory constraints, missing origin, invalid assertion composition. |
| Lowering | unsafe simplification, unsupported minimization, lost constraint trace. |
| Backend | unsupported backend capability, invalid backend expression, unsupported operator. |

## Expected Failure Examples

### Parser Failure

Mutation:

```text
Remove closing bracket from property declaration.
```

Expected classification:

```text
Expected rejection at Source → CST.
```

Incorrect behavior:

```text
Failure appears later during semantic validation.
```

### Semantic Failure

Mutation:

```text
Replace x.age with z.age where z is not declared by the LHS scope.
```

Expected classification:

```text
Expected rejection at AST → Semantic.
```

Incorrect behavior:

```text
Unresolved variable reaches IR1.
```

### IR Failure

Mutation:

```text
Drop one operand from an AND expression without marking the mutation as weakening.
```

Expected classification:

```text
Contract rejection or preservation violation.
```

Incorrect behavior:

```text
Mutation is accepted as equivalent.
```

### ModelBridge Failure

Mutation:

```text
Remove a feature from ModelSchema while the DSL references it.
```

Expected classification:

```text
Schema-semantic validation failure.
```

Incorrect behavior:

```text
Backend query is generated despite missing feature.
```

### Backend Boundary Failure

Mutation:

```text
Generate a backend query using an operator unsupported by the selected backend.
```

Expected classification:

```text
Backend capability rejection before execution.
```

Incorrect behavior:

```text
Backend runtime fails with an opaque error.
```

## Expected Failure Metadata

Each mutation should eventually declare:

```text
expected_layer: semantic
expected_failure: UnboundVariableError
expected_status: REJECTED
preserves_valid_ast: true
preserves_semantics: false
```

This metadata allows campaign reports to distinguish useful rejection from accidental failure.

## Failure Severity

| Severity | Meaning |
|---|---|
| Low | Diagnostic wording mismatch or minor report issue. |
| Medium | Failure occurs at wrong layer but still rejected safely. |
| High | Invalid artifact accepted into later pipeline stage. |
| Critical | Invalid backend query generated or verification result may be unsound. |

## P0 Requirement

At P0, expected failure definitions should exist for:

1. parser syntax failures;
2. builder structural failures;
3. semantic binding failures;
4. property-scope compatibility failures;
5. IR preservation violations;
6. ModelSchema inconsistencies;
7. schema-semantic mismatches;
8. backend capability mismatches.

## Guiding Principle

A failed mutation campaign is not necessarily bad.

A silent invalid success is worse than a clear failure.

FORML should prefer early, explicit, diagnosable rejection over late, ambiguous backend failure.
