# Specification Constants Contract

> Status: Accepted target contract — implementation pending  
> Scope: Source declaration through backend encoding  
> Priority: P0

## Purpose

This contract defines how specification constants cross Toetra compiler boundaries without being confused with scope variables, model features or backend solver variables.

Canonical example:

```toetra
model := "credit-risk.joblib"
target := default_risk

max_risk := 0.20
minimum_income := 25000.0

[LOGIC]:
forall applicant
    with domain(
        applicant.income: [minimum_income, 200000.0]
    )
    => target <= max_risk
    using Z3
```

## Cross-Layer Summary

| Boundary | Required representation or guarantee |
|---|---|
| Source | `identifier := scalar_literal` in the header. |
| CST | Declaration name and literal subtree are preserved. |
| AST | `SpecificationConstantDeclarationNode`; bare scalar names become `NameRefNode`. |
| Semantic | Declarations are registered globally; names are resolved by context and type checked. |
| SemanticValidatedAST | Every `NameRefNode` is classified as constant, implicit feature, or rejected. |
| IR1 | Constant references become typed constant expressions with source provenance. |
| IR2 | Constant values remain constants through normalization and assumption aggregation. |
| Backend | Literal is encoded directly; no unconstrained solver variable is created. |

## Source Contract

Specification constants:

- appear after required header declarations and before properties;
- are immutable;
- use unique non-reserved identifiers;
- accept scalar literals only in the initial profile;
- are visible to every property in the same program.

The source grammar does not decide whether a later bare name is a constant or an implicit feature.

## CST Contract

The parser preserves:

- declaration order;
- exact declaration identifier;
- literal token family;
- each bare identifier occurrence in scalar-expression position.

The CST must not substitute declared values into expressions.

## AST Contract

Target structural shape:

```text
HeaderNode(
    model: str,
    target: str,
    specification_constants: list[SpecificationConstantDeclarationNode],
)

SpecificationConstantDeclarationNode(
    name: str,
    value: ConstantNode,
)

NameRefNode(
    name: str,
)
```

Builder invariants:

- declaration values are typed literal nodes;
- source order is retained;
- a bare scalar name is not converted prematurely to an implicit `AttributeNode`;
- explicit `x0.feature` remains an `AttributeNode`;
- `target` remains a distinct `TargetRefNode`.

The builder does not reject duplicate declarations, scope collisions or incompatible uses unless the CST is structurally malformed.

## Semantic Registration Contract

Semantic validation first creates a program-level specification-constant table.

Each symbol contains at least:

```text
name
kind = SPECIFICATION_CONSTANT
value
dtype
declaration provenance
```

Registration rejects:

- duplicate names;
- reserved names;
- unsupported literal kinds;
- malformed declaration metadata.

Property validation then creates scope-local symbols. A scope variable whose name collides with a specification constant is rejected.

## Context-Aware Name Resolution

### Assertions

For a bare `NameRefNode(name)`:

```text
matching specification constant
    → resolved constant reference
else default entity exists
    → implicit feature reference
else
    → UnboundNameError
```

### Domain interval bounds

For a bare name:

```text
matching specification constant
    → resolved constant reference
otherwise
    → UnboundNameError
```

Input feature references in domain bounds must be explicit, for example `x0.b`.

### Finite-set members

For an unquoted identifier:

```text
matching specification constant
    → resolved constant value
otherwise
    → symbolic categorical literal
```

Quoted strings remain string literals.

### Explicit features

A qualified reference always denotes a feature:

```toetra
threshold := 7
[LOGIC]: forall x0 => x0.threshold <= threshold
```

This resolves to:

```text
feature x0.threshold <= specification constant threshold
```

## Type Contract

The constant preserves its declaration type:

| Source literal | Canonical type |
|---|---|
| `7` | `INT` |
| `0.20` | `FLOAT` |
| `true` | `BOOL` |
| `"EU"` | `STRING` |

Every use is type checked in context. Declaration success does not imply every use is valid.

Examples:

```toetra
max_risk := "low"
[LOGIC]: forall x0 => target <= max_risk
```

The declaration may be structurally valid, but numeric comparison must fail semantically.

## Semantic Annotation Contract

A resolved constant occurrence exposes metadata equivalent to:

```text
resolved_kind = SPECIFICATION_CONSTANT
resolved_symbol = <symbol>
resolved_type = <dtype>
resolved_value = <literal value>
```

An implicit feature occurrence exposes feature/entity metadata instead. Downstream lowering must never infer the category again from spelling.

## IR1 Lowering Contract

A specification-constant reference lowers to a constant-valued scalar IR node with provenance.

Conceptual form:

```text
ConstantExpressionIR(
    value=0.20,
    dtype=FLOAT,
    source_kind=SPECIFICATION_CONSTANT,
    source_name="max_risk",
)
```

Required guarantees:

- no unresolved `NameRefNode` reaches IR1;
- constant value and type are preserved;
- declaration name remains available for diagnostics;
- the constant is not represented as an input feature;
- the constant is not represented as a model output;
- the constant is not represented as a backend symbolic variable.

## IR2 and Aggregation Contract

Logical normalization treats a comparison containing specification constants as an ordinary atomic comparison.

Domain assumptions generated from constant bounds retain both:

- domain-entry provenance;
- specification-constant provenance for the bound value.

Constant folding is allowed only when semantics and provenance remain inspectable.

## Backend Contract

A backend receives the canonical literal value and type.

For Z3-oriented lowering:

```text
INT    → IntVal
FLOAT  → RealVal or exact canonical numeric encoding
BOOL   → BoolVal where supported
STRING → StringVal or declared categorical encoding where supported
```

Backend capability checks still apply. A valid string constant does not imply every numeric-only backend can use it.

## Diagnostics

Expected semantic diagnostics include:

| Condition | Diagnostic family |
|---|---|
| Duplicate declaration | `DuplicateSpecificationConstantError` |
| Reserved declaration name | `InvalidSpecificationConstantNameError` |
| Scope-variable collision | `SpecificationConstantScopeCollisionError` |
| Bare name unresolved | `UnboundNameError` |
| Incompatible use | `ScalarTypeMismatchError` |
| Unsupported declaration literal | `UnsupportedSpecificationConstantTypeError` |

Exact class names may evolve, but ownership by the semantic/type boundary must remain stable.

## Deferred Features

The initial contract deliberately excludes:

- derived constant expressions;
- references between constant declarations;
- declaration dependency graphs;
- cycle detection;
- local property constants;
- mutable reassignment;
- environment-variable interpolation;
- backend-specific declaration syntax.

These require separate decisions and must not be inferred from this contract.
