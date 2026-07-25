# Property-Based Testing

> Status: P0 — required testing layer  
> Implementation: planned / partially started through Hypothesis-oriented design  
> Scope: generated Toetra specifications, compiler contracts, semantic invariants, IR normalization, and regression discovery

## Purpose

Property-Based Testing is a core testing strategy for Toetra.

Toetra should not only be tested with hand-written examples. It must also be tested against many generated specifications, scopes, assertions, and model-schema combinations in order to discover edge cases that would not appear in manually curated fixtures.

The purpose of Property-Based Testing is to validate general properties of the compiler pipeline:

```text
For many valid Toetra programs:
    parsing succeeds;
    AST construction succeeds;
    semantic validation is deterministic;
    IR generation preserves semantic bindings;
    normalization preserves logical meaning.

For many invalid Toetra programs:
    rejection happens at the expected boundary;
    the failure category is stable;
    no unrelated layer crashes unexpectedly.
```

## Position in the Testing Strategy

Property-Based Testing complements golden samples and Miova campaigns.

| Testing approach | Main role |
|---|---|
| Unit tests | Validate small local behavior |
| Golden samples | Freeze explicit known examples |
| Property-Based Testing | Explore large valid/invalid input spaces |
| Miova campaigns | Mutate artifacts across pipeline boundaries |
| Intelligent fuzzing | Search adversarial or high-value perturbations |

Property-Based Testing should be used before and alongside Miova campaigns.

Hypothesis generates structured examples from strategies. Miova mutates artifacts and transformation boundaries. Together, they provide two complementary exploration mechanisms.

## Why Hypothesis

Hypothesis is useful for Toetra because the language has structured grammar, typed AST nodes, semantic scopes, and layered transformations.

Instead of writing only examples such as:

```toetra
model := "model.joblib"
target := label

[ROBUSTNESS]: forall baseline, candidate => CLASSIFICATION.EQUAL()
```

Toetra can generate families of valid and invalid specifications:

```text
valid property types
× valid scopes
× compatible assertions
× valid domains
× valid neighborhoods
× valid model schemas
× supported backends
```

This allows the compiler to be tested as a language-processing system, not only as a collection of fixtures.

## Generated Artifact Levels

Hypothesis strategies can target several layers.

| Layer | Strategy target | Purpose |
|---|---|---|
| Source | `.toetra` strings | Validate parser and grammar acceptance |
| CST | Lark trees | Validate builder assumptions |
| AST | AST dataclasses | Validate semantic layer independently from parser |
| Semantic AST | annotated AST | Validate IR lowering assumptions |
| IR1 | logical IR trees | Validate NNF and normalization invariants |
| ModelSchema | model metadata | Validate schema-semantic compatibility |
| Aggregated assertions | logical constraint sets | Validate aggregation and lowering contracts |

The recommended order is:

```text
1. generate source strings;
2. generate AST directly;
3. generate IR1 directly;
4. generate ModelSchema directly;
5. combine generated DSL artifacts with generated model schemas.
```

## Valid Generation

Valid generators should only produce artifacts that satisfy the contract of their target layer.

Examples:

| Strategy | Expected guarantee |
|---|---|
| `valid_property_type()` | returns a known property enum |
| `valid_scope_for_property(property)` | returns a compatible scope |
| `valid_attribute_for_scope(scope)` | references a resolvable entity or implicit entity |
| `valid_comparison()` | produces a typed comparison leaf |
| `valid_problem_function(problem)` | produces a compatible problem/function pair |
| `valid_model_schema()` | produces a schema with target and features |
| `valid_ir1_logical_tree()` | produces a backend-independent logical tree |

Valid generation is used to assert that Toetra accepts what it is supposed to accept.

## Invalid Generation

Invalid generators intentionally produce artifacts that violate known constraints.

Examples:

| Invalid case | Expected rejection layer |
|---|---|
| missing model declaration | parser / builder |
| unknown property type | builder / semantic |
| incompatible property and scope | semantic |
| unresolved variable | semantic binding |
| invalid problem/function pair | semantic logic |
| missing semantic annotation before IR1 | semantic-to-IR1 |
| invalid feature name against ModelSchema | schema-to-semantic |
| malformed IR1 logical tree | IR1 invariant |

Invalid generation is useful only when the expected rejection boundary is clear.

## Core Properties to Test

### 1. Parser Determinism

For every generated valid source:

```text
parse(source) == parse(source)
```

The parser should produce deterministic CSTs for the same input.

### 2. Builder Totality on Valid CST

For every CST produced from a valid source:

```text
build(parse(source)) produces AST
```

No valid CST should produce an unexpected builder crash.

### 3. Semantic Acceptance of Compatible Properties

For every generated valid AST where property/scope/problem/function are compatible:

```text
semantic_validate(ast) succeeds
```

### 4. Semantic Rejection of Incompatible Properties

For every generated AST with an intentionally incompatible property/scope pair:

```text
semantic_validate(ast) rejects with semantic failure
```

### 5. Binding Preservation into IR1

For every semantic-validated AST:

```text
semantic.resolved_entity is preserved into ComparisonIR.entity
semantic.resolved_path is preserved into ComparisonIR.feature/path
```

IR1 must not re-infer bindings from raw syntax when semantic annotations already exist.

### 6. IR1 NNF Invariant

For every generated logical tree lowered to IR1-NNF:

```text
NOT nodes may only appear directly above atomic predicates
```

If Toetra eliminates implication before NNF, then:

```text
IR1-NNF contains no ImplyIR
```

If implication is temporarily retained, the document must mark this as a transitional status.

### 7. IR2 Normal-Form Invariant

For every IR1 converted to IR2-CNF:

```text
IR2 is a conjunction of clauses;
each clause is a disjunction of literals.
```

For every IR1 converted to IR2-DNF:

```text
IR2 is a disjunction of cases;
each case is a conjunction of literals.
```

### 8. Shrinkability

When a generated example fails, Hypothesis should shrink it to a minimal counterexample.

This is strategically important for Toetra because minimal failing DSL snippets become high-quality regression tests and golden samples.

## Example Test Families

Recommended property-based test families:

```text
test_valid_sources_parse
test_valid_sources_build_ast
test_valid_programs_semantically_validate
test_invalid_bindings_fail_at_semantic_layer
test_property_scope_compatibility_matrix
test_problem_function_compatibility_matrix
test_semantic_bindings_are_preserved_in_ir1
test_ir1_nnf_invariant
test_ir2_cnf_shape_invariant
test_ir2_dnf_shape_invariant
test_model_schema_feature_references
test_model_schema_task_compatibility
```

## Relationship with Miova

Hypothesis and Miova should not be confused.

| Tooling | Main object | Main question |
|---|---|---|
| Hypothesis | generated examples | Does Toetra satisfy a property over many generated cases? |
| Miova | mutated artifacts | Does Toetra remain robust when artifacts are transformed or corrupted? |

A strong Toetra testing strategy can combine both:

```text
Hypothesis generates valid Toetra programs.
Miova mutates the resulting AST, Semantic AST, IR1, IR2, or ModelSchema.
Toetra checks whether each mutation is accepted, rejected, skipped, or fails unexpectedly.
```

## Non-Goals

Property-Based Testing does not replace:

- grammar golden samples;
- explicit contract tests;
- backend-specific solver tests;
- Miova mutation campaigns;
- formal proof of logical equivalence.

It provides broad exploration and counterexample discovery, not full formal verification.

## Success Criteria

Property-Based Testing is effective when:

- generated examples cover all major DSL constructs;
- invalid examples fail at the expected layer;
- failing examples shrink to readable minimal cases;
- discovered bugs become regression tests;
- strategies are aligned with compiler contracts;
- generated artifacts do not bypass the layer they are meant to test.

---

## Quantified Domain and Arithmetic Strategies

Recommended Hypothesis strategies:

```text
quantified_identifier()
quantifier_kind()
interval_boundary_kind()
non_empty_numeric_interval()
finite_numeric_set(min_size=1)
finite_symbolic_set(min_size=1)
scalar_constant()
feature_ref(bound_entities)
affine_scalar_expression()
nonlinear_scalar_expression()
comparison_expression()
typed_domain(bound_entity)
```

Required properties include:

1. Every generated valid quantified source preserves its identifier through AST and semantic scope.
2. Replacing the declared entity in one explicit reference with a fresh identifier causes semantic rejection.
3. Every interval delimiter pair maps to the expected strict/non-strict operators.
4. Domain expansion is logically equivalent to membership for sampled numeric valuations.
5. Arithmetic parsing respects precedence independently of whitespace and redundant parentheses.
6. Affine classification is invariant under parenthesization that preserves the same tree meaning.
7. Symbolic products are never misclassified as affine.
8. Generated literal-zero divisions are always rejected before backend translation.
9. Normal-form conversion never descends into or mutates scalar-expression internals.
10. Capability rejection remains deterministic for the same requirements/backend registry.

Shrunk failures should be promoted to the invalid or golden-sample catalog.
