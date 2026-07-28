# Unit Tests

> Status: Implemented and required
> Implementation: partially implemented  
> Scope: isolated functions, small classes, local invariants

## Purpose

Unit tests validate the smallest meaningful Toetra behaviors.

They should be fast, deterministic, and isolated. A unit test should not require the full
compiler pipeline unless the behavior under test explicitly depends on it.

## Unit Test Goals

Unit tests should prove that each local component respects its own responsibility:

| Component | Unit Test Focus |
|---|---|
| grammar vocabulary | enum normalization, protected words, operators |
| parser helpers | grammar loading, parser creation |
| builder utilities | tree navigation, token extraction, strict value extraction |
| AST builders | node construction, missing child rejection |
| semantic validators | binding, scope creation, compatibility rules |
| IR translators | node-to-node conversion, operator preservation |
| ModelBridge loaders | extension selection, deserialization error handling |
| ModelBridge detector | framework classification |
| ModelBridge introspectors | schema extraction and metadata normalization |

## Parser Unit Tests

Parser unit tests should validate:

- valid source is accepted;
- invalid syntax is rejected;
- comments and whitespace do not change parse meaning;
- grammar path resolution is stable;
- parser code does not depend on test fixtures at runtime.

Example test families:

```text
test_parser_accepts_valid_minimal_property
test_parser_rejects_missing_header
test_parser_rejects_invalid_property_imply
test_parser_handles_comments
test_parser_handles_multiple_properties
```

## Builder Unit Tests

Builder unit tests should validate:

- strict extraction of required nodes;
- correct `HeaderNode` construction;
- correct `PropertyNode` construction;
- correct LHS mode detection;
- correct RHS assertion extraction;
- correct comparison, problem, and logical node construction;
- correct unary/binary arithmetic tree construction;
- preservation of arithmetic precedence and associativity.

Important builder invariants:

```text
CST input must not leak Lark implementation details into AST semantics.
Missing required nodes must fail early.
AST nodes must be explicit and typed.
```

## AST Unit Tests

AST unit tests should validate:

- all semantic-capable nodes expose semantic annotations or have a clear reason not to;
- primitive nodes follow the expected shape;
- program and property nodes are stable containers;
- assertion nodes preserve logical tree structure.

Potential stabilization issue:

```text
Some AST nodes currently inherit from ASTNode while some containers/primitives do not.
This must be either standardized or documented as an intentional boundary.
```

## Semantic Unit Tests

Semantic unit tests should validate:

- `check_at` creates pointwise context;
- `at` creates local anchor/perturbation context;
- `pairwise` creates anchor/perturbation context;
- `forall <identifier>` and `exists <identifier>` introduce the declared symbolic variable;
- implicit feature access resolves to the correct default entity;
- explicit variables are resolved via symbol table;
- ambiguous implicit references are rejected;
- property/scope compatibility is enforced;
- arithmetic operands are recursively bound and typed;
- literal-zero division and target-in-domain are rejected;
- affine and nonlinear requirements are classified.

Example test families:

```text
test_at_scope_introduces_anchor_and_perturbation
test_check_at_uses_anchor_as_default_entity
test_pairwise_requires_primed_right_variable
test_quantifier_requires_identifier
test_quantifier_preserves_declared_identifier
test_quantifier_rejects_mismatched_explicit_entity
test_quantifier_accepts_target_only_assertion
test_implicit_attribute_resolves_to_default_entity
test_ambiguous_attribute_without_default_entity_fails
test_property_scope_compatibility
```

## IR Unit Tests

IR unit tests should validate:

- `ComparisonNode` becomes a symmetric expression-to-expression `ComparisonIR`;
- scalar AST nodes lower recursively to scalar IR nodes;
- arithmetic tree structure is preserved through logical normalization;
- comparison operators are preserved;
- logical operators are preserved or normalized according to the IR layer;
- semantic entity resolution is preserved;
- scopes are correctly translated;
- unsupported nodes fail explicitly.

Example test families:

```text
test_comparison_translation_preserves_operator
test_arithmetic_precedence_builds_expected_ast
test_expression_to_expression_comparison_lowers_to_ir1
test_arithmetic_domain_bound_preserves_boundary_and_expression
test_symbolic_product_requires_nonlinear_capability
test_at_scope_translation_contains_anchor_and_perturbation
test_pairwise_translation_splits_on_tilde
test_implicit_attribute_uses_semantic_resolution
test_problem_node_translation_preserves_problem_and_function
```

## ModelBridge Unit Tests

ModelBridge unit tests should validate:

- loader factory selects the correct loader by extension;
- unsupported extensions fail;
- detector recognizes supported frameworks;
- unsupported models fail;
- introspectors produce a normalized `ModelSchema`;
- feature dtypes are mapped to Toetra semantic types;
- framework-specific metadata does not break normalized schema shape.

Example test families:

```text
test_loader_factory_selects_joblib_loader
test_loader_factory_rejects_unknown_extension
test_detector_recognizes_sklearn_model
test_sklearn_introspector_builds_model_schema
test_xgboost_introspector_overrides_framework
```

## Test Quality Rules

Unit tests should be:

- deterministic;
- small;
- independent;
- explicit about expected errors;
- not dependent on global mutable state unless that state is part of the behavior tested.

## Non-Goals

Unit tests should not attempt to prove:

- full end-to-end verification;
- solver correctness;
- backend completeness;
- large-scale runtime behavior.

Those are covered by higher-level tests.

---

## Language Evolution Unit-Test Minimum

The migration is not complete without isolated unit tests for:

- quantifier token and identifier extraction;
- interval delimiter to `OPEN`/`CLOSED` normalization;
- finite-set literal typing;
- arithmetic precedence and associativity;
- unary expression construction;
- recursive feature binding inside scalar expressions;
- strict rejection of explicit entity mismatch;
- duplicate-domain detection;
- interval emptiness/order validation;
- affine/nonlinear/symbolic-division classification;
- literal division-by-zero detection;
- domain-to-assumption operator selection;
- requirements computation;
- solver-result interpretation by verification semantics;
- specification-constant declaration extraction and literal typing;
- `NameRefNode` construction without premature binding;
- constant-first bare-name resolution;
- scope-variable collision and duplicate declaration rejection;
- constant provenance preservation through IR1/IR2;
- backend literal encoding without solver-variable creation.

A unit test should target one responsibility. Full source-to-solver behavior belongs to end-to-end tests.


## Language-Evolution File Split

The parser portion should remain split as:

```text
tests/unit/parser/
├── conftest.py
├── test_grammar_generation.py
├── test_quantified_scopes.py
├── test_typed_domains.py
├── test_arithmetic_expressions.py
├── test_specification_constants.py
└── test_parser_regressions.py
```

Do not recreate a monolithic `test_language_evolution_g1.py`. The same feature-oriented split applies downstream.

Parser and source-driven tests use complete programs. Tests of pure helpers may use isolated nodes or fragments when the test name and fixture make that boundary explicit.
