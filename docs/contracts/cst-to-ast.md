# CST to AST Contract

> Status: Implemented and accepted
> Scope: Concrete Syntax Tree to typed Toetra AST
> Audience: builder maintainers, AST maintainers and mutation authors

## Purpose

The builder removes parser-specific structure while preserving every semantically relevant part of the source.

---

## Input and Output

```text
Input:  official Toetra CST
Output: ProgramNode AST
```

No raw Lark node is required downstream after a successful build.

---

## Quantifier Mapping

Source:

```toetra
forall x0
```

Target conceptual node:

```text
QuantifierExprNode(
    quantifier=FORALL,
    variable="x0",
    domain=None,
)
```

The builder:

- canonicalizes the quantifier vocabulary;
- preserves the exact identifier text;
- does not invent `_x`;
- does not check assertion binding;
- rejects a CST shape lacking the required identifier.

---

## Domain Mapping

Source:

```toetra
with domain(
    x0.a: ]0.0, 3.0],
    x0.region: {EU, US}
)
```

Conceptual AST:

```text
DomainNode(entries=[
    DomainEntryNode(
        subject=AttributeNode(path=["x0", "a"]),
        constraint=IntervalDomainNode(
            lower=ConstantNode(0.0),
            upper=ConstantNode(3.0),
            lower_boundary=OPEN,
            upper_boundary=CLOSED,
        ),
    ),
    DomainEntryNode(
        subject=AttributeNode(path=["x0", "region"]),
        constraint=FiniteSetDomainNode(values=[
            SymbolicCategoryNode("EU"),
            SymbolicCategoryNode("US"),
        ]),
    ),
])
```

The builder preserves:

- subject path;
- entry order;
- bound expression trees;
- boundary kinds;
- set member order and literal kind;
- source location when available.

It must not flatten a domain into `name + raw values`.

---

## Scalar Expression Mapping

Required conceptual mappings:

```text
literal               → ConstantNode
qualified/unqualified feature → AttributeNode
target keyword        → TargetRefNode
unary arithmetic      → UnaryArithmeticNode
binary arithmetic     → BinaryArithmeticNode
comparison            → ComparisonNode(left_expr, op, right_expr)
```

The builder preserves precedence, associativity and operand order.

Parentheses may disappear as nodes when their grouping is fully represented by the resulting tree.

---

## Structural Guarantees

A successful build guarantees:

- every property has a scope and assertion;
- every quantified scope has a variable field;
- every comparison has two scalar operands;
- every unary/binary expression has the required operands;
- every domain entry has one explicit subject and one typed constraint;
- no solver-native type appears in the AST;
- controlled vocabulary is canonicalized at the builder boundary where documented.

---

## Builder Non-Goals

The builder does not:

- resolve input symbols;
- apply default entities;
- validate interval ordering;
- reject duplicate domain subjects;
- validate arithmetic operand types;
- decide backend support;
- expand domain entries into boolean formulas.

---

## Builder-Owned Failures

The builder rejects CST shapes that are syntactically accepted but structurally impossible to map, including:

- missing quantified variable subtree;
- missing domain subject or constraint;
- interval with absent bound node;
- finite-set member that cannot be represented as a literal;
- arithmetic operator with missing operand;
- comparison with fewer or more than two scalar operands;
- unrecognized protected vocabulary after normalization.

## Header and argument preservation

The header builder preserves:

```text
model declaration   → HeaderNode.model
target declaration  → HeaderNode.target
dataset declaration → HeaderNode.dataset | None
constant declarations → ordered HeaderNode.specification_constants
anchor declarations → ordered ProgramNode.anchors
```

Header artifact declarations are not resolved at this boundary. File-relative
resolution belongs to runtime planning. Anchors remain program-level nodes
because they enter the shared point environment rather than model metadata.

Generic grammar arguments must never disappear during AST construction:

- backend `name=value` arguments become ordered typed `ArgNode` entries;
- duplicate or positional backend arguments fail explicitly;
- non-empty problem-function arguments fail explicitly because their semantics
  are not defined;
- legacy-neighborhood arguments become ordered typed `ArgNode` entries, while
  positional or duplicate entries fail explicitly.

See the [DSL information preservation contract](dsl-information-preservation.md).

## Specification Constant Addendum

For header declarations and bare scalar names, the builder must produce:

```text
identifier := literal
    → SpecificationConstantDeclarationNode

bare identifier in scalar expression
    → NameRefNode
```

It must not:

- substitute declaration values;
- resolve names against declarations;
- apply implicit-feature fallback;
- reject declaration/scope collisions;
- create backend constants or variables.

Those responsibilities belong to semantic validation and IR lowering.
