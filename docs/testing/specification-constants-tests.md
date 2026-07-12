# Specification Constants Test Plan

> Status: Accepted implementation plan  
> Scope: Parser through backend for immutable program-level specification constants  
> Rule: Program-level fixtures are primary; fragments are auxiliary only

## Purpose

This document defines how tests for specification constants are split by compiler responsibility.

The feature must not be implemented through one monolithic test file. Each layer owns a distinct contract and receives complete `.forml` programs through its public entry point whenever the layer starts from source.

## Primary Test Rule

A parser or pipeline test must use a complete program:

```forml
model := "credit-risk.joblib"
target := default_risk

max_risk := 0.20

[LOGIC]: forall applicant => target <= max_risk
```

This is not sufficient as the primary parser test:

```text
target <= max_risk
```

Fragments are acceptable only for:

- lexer/token unit tests;
- EBNF generator helper tests;
- pure AST construction helpers receiving an already isolated CST node;
- pure semantic or IR functions whose input artifact is explicitly constructed.

## Recommended File Split

```text
test/unit/parser/
├── conftest.py
├── test_grammar_generation.py
├── test_quantified_scopes.py
├── test_typed_domains.py
├── test_arithmetic_expressions.py
├── test_specification_constants.py
└── test_parser_regressions.py

test/unit/builder/
├── test_quantified_scopes.py
├── test_typed_domains.py
├── test_scalar_expressions.py
├── test_specification_constants.py
└── test_name_references.py

test/unit/semantic/
├── test_quantified_bindings.py
├── test_domain_bindings.py
├── test_scalar_expression_types.py
├── test_specification_constant_registration.py
├── test_name_resolution.py
└── test_specification_constant_types.py

test/unit/ir/ir1/
├── test_scalar_expression_lowering.py
├── test_typed_domain_lowering.py
└── test_specification_constant_lowering.py

test/unit/ir/ir2/
├── test_domain_assumptions.py
├── test_requirements.py
└── test_specification_constant_provenance.py

test/integration/
├── test_specification_constants_pipeline.py
└── test_specification_constants_z3.py
```

A repository may use slightly different directories, but it must preserve this separation of responsibilities.

## Parser Suite

Target file:

```text
test/unit/parser/test_specification_constants.py
```

Mandatory complete-program cases:

| ID | Program behavior | Expected |
|---|---|---|
| PAR-SPC-001 | integer constant declaration | parse |
| PAR-SPC-002 | float constant declaration | parse |
| PAR-SPC-003 | boolean constant declaration | parse |
| PAR-SPC-004 | string constant declaration | parse |
| PAR-SPC-005 | multiple declarations before properties | parse and preserve order in CST |
| PAR-SPC-006 | constant name used in assertion | parse without resolving the name |
| PAR-SPC-007 | constant in interval bound | parse |
| PAR-SPC-008 | constant in finite set | parse |
| PAR-SPC-009 | expression on declaration RHS | reject in initial profile |
| PAR-SPC-010 | missing declaration value | reject |

Parser assertions should inspect the relevant CST shape, not only `tree is not None`.

## Builder Suite

Target files:

```text
test/unit/builder/test_specification_constants.py
test/unit/builder/test_name_references.py
```

Mandatory cases:

| ID | Expected AST invariant |
|---|---|
| AST-SPC-001 | `HeaderNode.specification_constants` preserves source order |
| AST-SPC-002 | declaration literal becomes a typed `ConstantNode` |
| AST-SPC-003 | bare scalar identifier becomes `NameRefNode` |
| AST-SPC-004 | `x0.threshold` remains `AttributeNode` |
| AST-SPC-005 | `target` remains `TargetRefNode` |
| AST-SPC-006 | finite-set identifier remains unresolved/symbolic-capable until semantics |

The builder must not apply the constant-first resolution rule.

## Semantic Suite

Target files:

```text
test/unit/semantic/test_specification_constant_registration.py
test/unit/semantic/test_name_resolution.py
test/unit/semantic/test_specification_constant_types.py
```

Mandatory cases:

| ID | Expected semantic result |
|---|---|
| SEM-SPC-001 | unique constants register globally |
| SEM-SPC-002 | duplicate declaration rejected |
| SEM-SPC-003 | reserved name rejected |
| SEM-SPC-004 | collision with quantified/scope variable rejected |
| SEM-SPC-005 | bare name resolves to matching constant before implicit feature |
| SEM-SPC-006 | absent constant falls back to implicit feature in assertion |
| SEM-SPC-007 | explicit feature wins by syntax (`x0.threshold`) |
| SEM-SPC-008 | domain bound accepts matching constant |
| SEM-SPC-009 | domain bound rejects unknown bare feature name |
| SEM-SPC-010 | finite-set name resolves to constant when declared |
| SEM-SPC-011 | undeclared finite-set identifier remains symbolic categorical literal |
| SEM-SPC-012 | incompatible constant use rejected by type validation |

## IR1 and IR2 Suites

Mandatory cases:

| ID | Expected invariant |
|---|---|
| IR1-SPC-001 | resolved reference becomes constant-valued scalar IR |
| IR1-SPC-002 | value, dtype and `source_name` are preserved |
| IR1-SPC-003 | no unresolved `NameRefNode` reaches IR1 |
| IR2-SPC-001 | normalization keeps constant inside the atomic comparison |
| IR2-SPC-002 | domain assumptions retain constant declaration provenance |
| IR2-SPC-003 | constant folding, when performed, remains traceable |

## Backend and Integration Suites

Mandatory cases:

| ID | Expected behavior |
|---|---|
| BE-SPC-001 | numeric constant lowers to backend literal, not solver variable |
| BE-SPC-002 | boolean/string constants use capability-aware encoding |
| BE-SPC-003 | unsupported categorical constant use is rejected before solving |
| E2E-SPC-001 | reusable numeric threshold participates in universal proof |
| E2E-SPC-002 | changed threshold produces a counterexample |
| E2E-SPC-003 | same constant is reusable across two properties |

## Fixture Organization

Complete source programs should be reusable through named fixtures or source constants, for example:

```text
test/fixtures/forml/specification_constants/
├── valid_numeric_threshold.forml
├── valid_feature_name_collision.forml
├── valid_domain_bound.forml
├── valid_finite_set.forml
├── invalid_duplicate.forml
├── invalid_scope_collision.forml
├── invalid_non_literal_rhs.forml
└── unsupported_categorical_backend.forml
```

Small inline triple-quoted programs are also acceptable when they remain readable and are used by only one test.

## Regression Rule

The existing G1 parser split remains intact. Specification-constant parser tests are added as a dedicated file; they are not merged back into a generic `test_language_evolution.py` file.

## Exit Criteria

The specification-constant extension is ready to leave a gate only when:

- its layer-specific suite is green;
- all previous gate suites remain green;
- complete programs reach the intended boundary;
- failures are asserted by diagnostic family, not only by broad exception type;
- no backend variable is created for an immutable specification constant.
