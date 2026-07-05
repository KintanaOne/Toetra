# Golden Samples

> Status: P0 — required  
> Implementation: planned  
> Scope: stable source examples and expected artifacts

## Purpose

Golden samples are canonical FORML examples used to freeze expected compiler behavior.

They are not random test. They are reference cases that define what FORML is expected to
accept, reject, transform, and preserve.

## Why Golden Samples Matter

FORML has many layers:

```text
Source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1
→ IR2
→ AggregatedAssertionSet
→ BackendQuery
```

A small grammar or semantic change can affect several downstream artifacts. Golden samples
make those changes explicit.

## Golden Sample Categories

| Category | Purpose |
|---|---|
| valid minimal | smallest valid FORML program |
| valid local robustness | `at x` with neighborhood |
| valid pointwise bound | `check_at x` with comparison |
| valid pairwise monotonicity | `x ~ x'` relation |
| valid quantifier | `forall` / `exists` properties |
| valid logical composition | AND/OR/NOT/IMPLY precedence |
| valid problem predicate | `CLASSIFICATION.EQUAL()` |
| invalid syntax | parser rejection |
| invalid binding | semantic rejection |
| invalid scope/property | compatibility rejection |
| invalid model schema | schema-aware rejection |
| mutation boundary | Miova expected failures |

## Recommended Directory Structure

```text
tests/golden/
  source/
    valid/
    invalid/
  ast/
  semantic/
  ir1/
  ir2/
  model-schema/
  aggregated/
  backend-query/
```

## Golden Sample Format

Each golden sample should include:

```text
sample_name.forml
expected.json
metadata.yaml
```

Example metadata:

```yaml
name: local_robustness_l2
status: valid
property: ROBUSTNESS
scope: local
expected_layers:
  parser: pass
  builder: pass
  semantic: pass
  ir1: pass
  ir2: planned
  backend: planned
```

## P0 Golden Samples

### 1. Minimal valid program

Purpose:

```text
Validate that the smallest supported FORML source can pass parser, builder, semantic, and IR1.
```

Should cover:

- model declaration;
- target declaration;
- one property;
- one simple assertion;
- no backend declaration.

### 2. Local robustness with neighborhood

Purpose:

```text
Validate local scope with anchor/perturbation semantics.
```

Should cover:

- `at x`;
- implicit `x'`;
- neighborhood metric;
- epsilon parameter;
- comparison or problem predicate;
- IR scope variables.

### 3. Pointwise bound

Purpose:

```text
Validate check_at scope and BOUND property compatibility.
```

Should cover:

- `check_at x`;
- default entity `x`;
- numeric comparison;
- pointwise scope.

### 4. Pairwise monotonicity

Purpose:

```text
Validate pairwise semantics and primed variable rules.
```

Should cover:

- `x ~ x'`;
- pairwise neighborhood;
- anchor/perturbation roles;
- monotonicity property compatibility.

### 5. Quantifier property

Purpose:

```text
Validate symbolic variable introduction.
```

Should cover:

- `forall` or `exists`;
- internal `_x`;
- domain restriction;
- implicit feature resolution.

### 6. Logical precedence

Purpose:

```text
Validate parser/builder logical precedence and AST/IR structure.
```

Should cover:

- parentheses;
- AND;
- OR;
- NOT;
- implication;
- nested expressions.

### 7. Problem predicate

Purpose:

```text
Validate problem/function compatibility.
```

Should cover:

- classification/regression problem;
- allowed function;
- invalid function rejection.

### 8. Backend declaration

Purpose:

```text
Validate backend syntax parsing without backend execution.
```

Should cover:

- backend name;
- backend args;
- backend normalization;
- backend boundary preparation.

### 9. ModelBridge schema

Purpose:

```text
Validate a model artifact becomes normalized ModelSchema.
```

Should cover:

- supported model format;
- supported framework;
- feature schema;
- target;
- task metadata.

### 10. Schema-aware semantic validation

Purpose:

```text
Validate that DSL feature references are checked against ModelSchema.
```

Should cover:

- valid feature reference;
- missing feature;
- dtype mismatch;
- task/property compatibility.

## Invalid Golden Samples

Invalid samples are as important as valid samples.

They should cover:

| Invalid Case | Expected Boundary |
|---|---|
| missing model declaration | parser or builder |
| missing target declaration | parser or builder |
| malformed property section | parser |
| unsupported property/scope pair | semantic |
| unknown variable | semantic binding |
| ambiguous implicit attribute | semantic binding |
| invalid problem/function pair | semantic |
| unknown model format | ModelBridge loading |
| unsupported model framework | ModelBridge detection |
| missing feature metadata | ModelBridge introspection |
| missing model feature reference | schema-semantic boundary |
| unsupported backend capability | backend boundary |

## Golden Artifact Stability

Golden expected outputs should avoid unstable values:

- memory addresses;
- object reprs;
- ordering that is not semantically relevant;
- framework-specific values not guaranteed by the model.

Expected artifacts should prefer normalized dictionaries or snapshots.

## Golden Samples and Miova

Miova campaigns should use golden samples as seeds.

Recommended strategy:

```text
golden valid source
→ mutate source/CST/AST/IR
→ verify expected layer behavior
```

Examples:

- mutate a valid property type;
- remove a required LHS variable;
- corrupt a resolved semantic binding;
- flip a comparison operator;
- mutate IR1 logical structure;
- remove a ModelSchema feature.

## Success Criteria

Golden samples are sufficient when:

- each supported property has at least one valid example;
- each supported scope has at least one valid example;
- each critical failure boundary has at least one invalid example;
- each sample has expected parser/builder/semantic/IR outcomes;
- future changes can be reviewed through snapshot diffs.
