# Contract Testing

> Status: planned / critical  
> Scope: using Miova to validate FORML layer contracts  
> Audience: maintainers, test engineers, compiler contributors

## Purpose

Contract testing verifies that each FORML layer respects its declared input and output obligations.

Miova uses mutations to actively challenge those obligations.

A contract test does not only ask:

```text
Does this layer work on normal examples?
```

It asks:

```text
Does this layer behave correctly when its assumptions are challenged?
```

## Contract Structure

Each FORML boundary contract should define:

- accepted input artifact kind;
- produced output artifact kind;
- preconditions;
- postconditions;
- preservation guarantees;
- expected failures;
- forbidden silent behavior;
- diagnostic requirements.

## Generic Contract Template

```text
Contract: <Layer A> → <Layer B>

Input artifact:
    <kind>

Output artifact:
    <kind>

Preconditions:
    - ...

Postconditions:
    - ...

Preservation:
    - ...

Expected failures:
    - ...

Forbidden behavior:
    - ...
```

## Contract Test Classes

### Validity Preservation

Checks that a mutation preserves the validity expected by the target layer.

Example:

```text
Reordering operands in an AND node should preserve logical validity.
```

### Expected Rejection

Checks that an invalid mutation is rejected by the correct boundary.

Example:

```text
Unknown variable introduced in AST should fail during semantic binding.
```

### Diagnostic Stability

Checks that failures are classified at the correct layer.

Example:

```text
A grammar error should not become a backend error.
```

### Semantic Preservation

Checks whether transformed artifacts preserve meaning.

Example:

```text
NOT (A AND B) → (NOT A OR NOT B)
```

### Equisatisfiability Tracking

Checks transformations that may not preserve strict syntactic equivalence but preserve satisfiability.

Example:

```text
Certain CNF transformations may introduce auxiliary structure.
```

## Boundary Contract Targets

| Contract | Miova Role |
|---|---|
| Source → CST | Mutate raw syntax and check parser classification. |
| CST → AST | Mutate tree structure and check builder strictness. |
| AST → Semantic | Mutate variables, scopes, and properties. |
| Semantic → IR1 | Mutate semantic annotations and logical roots. |
| IR1 → IR2 | Mutate logical structure and check normal-form guarantees. |
| Model → Schema | Mutate model metadata and framework assumptions. |
| Schema → Semantic | Mutate features and task metadata. |
| Assertion Aggregation | Mutate assertion sets and constraint composition. |
| Lowering | Mutate simplification/minimization assumptions. |
| IR → Backend | Mutate backend capability constraints. |

## Example: AST → Semantic Contract Test

Input:

```text
AST property using implicit feature access: age <= 30
```

Mutation:

```text
Change LHS scope from `at x` to a pairwise scope with ambiguous variables.
```

Expected result:

```text
Semantic validation rejects ambiguity or resolves according to explicit default entity rules.
```

The test passes only if the outcome matches the declared contract.

## Example: IR1 Contract Test

Input:

```text
NOT (A AND B)
```

Mutation or transformation:

```text
Apply De Morgan normalization.
```

Expected result:

```text
(NOT A) OR (NOT B)
```

Contract expectations:

- no semantic binding is lost;
- output remains valid IR1;
- transformation is traceable;
- logical equivalence is preserved.

## Forbidden Silent Behavior

The most dangerous outcome is not failure.

The most dangerous outcome is silent acceptance of an invalid artifact.

FORML contract testing must reject:

- unresolved attributes accepted as valid;
- invalid model features accepted silently;
- backend-incompatible queries sent to backend;
- logical weakening without explicit classification;
- mutation-induced contradictions ignored by aggregation.

## Contract Test Reports

A contract test report should include:

- contract name;
- mutation name;
- input artifact kind;
- output artifact kind;
- expected outcome;
- actual outcome;
- violated guarantee if any;
- diagnostic classification.

## P0 Requirement

P0 contract testing must prioritize:

1. AST → Semantic;
2. Semantic → IR1;
3. IR1 → IR2;
4. Model → Schema;
5. Schema → Semantic;
6. Assertion Aggregation;
7. Lowering → Backend.
