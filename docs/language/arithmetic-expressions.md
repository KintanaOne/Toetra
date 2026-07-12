# Arithmetic Expressions

> Status: Target contract accepted for documentation-first implementation  
> Scope: Numeric expressions in assertions and interval bounds  
> Priority: P0  
> Audience: DSL users, compiler contributors, semantic validators, IR and backend authors

## Purpose

FORML arithmetic expressions allow users to express relations between model inputs, model outputs, and numeric constants without embedding backend-specific syntax.

Examples:

```forml
x0.revenue - x0.cost >= 0
2 * x0.a + x0.b <= target
(target - x0.baseline) / 2 <= 7
```

Arithmetic expressions may also appear as bounds of a typed numeric interval:

```forml
with domain(
    x0.a: [x0.b - 1.0, x0.b + 1.0]
)
```

Arithmetic is a scalar-expression concern. Boolean operators continue to compose complete predicates.

---

## Core Design Decision

A comparison is generalized from:

```text
attribute comparison_operator constant
```

to:

```text
scalar_expression comparison_operator scalar_expression
```

Conceptually:

```text
ComparisonNode(
    left: ScalarExpressionNode,
    op: EnumComparisonOperator,
    right: ScalarExpressionNode,
)
```

This makes feature-to-feature, target-to-expression, and expression-to-expression relations first-class.

---

## Expression Leaves

A scalar expression may contain:

| Leaf | Example | Meaning |
|---|---|---|
| Numeric literal | `3`, `0.5` | Typed numeric literal. |
| Specification constant | `max_risk`, `tolerance` | Immutable scalar declared in the header. |
| Input feature | `x0.a`, `a` | Explicit or implicitly bound feature reference. |
| Model output | `target` | Output declared by the program header. |
| Parenthesized expression | `(x0.a + x0.b)` | Explicit grouping. |

String and boolean literals or specification constants remain valid comparison operands for compatible equality checks, but they cannot participate in arithmetic operators.

```forml
x0.segment == "A"
x0.enabled != false
```

---

## Operators

| Operator | Meaning | Associativity |
|---|---|---|
| unary `+` | Numeric identity | right |
| unary `-` | Numeric negation | right |
| `*` | Multiplication | left |
| `/` | Division | left |
| `+` | Addition | left |
| `-` | Subtraction | left |

The initial language does not include exponentiation, modulo, implicit multiplication, or arithmetic functions such as `abs`, `min`, `max`, `log`, and `exp`.

---

## Precedence

From strongest to weakest:

```text
parenthesized scalar expression
unary + and -
multiplication and division
addition and subtraction
comparison
NOT
AND
OR
logical implication
```

Therefore:

```forml
x0.a + 2 * x0.b <= target
```

means:

```text
x0.a + (2 * x0.b) <= target
```

Comparison operators are not associative. Chained comparisons are rejected:

```forml
0 <= x0.a <= 3
```

The equivalent valid assertion is:

```forml
0 <= x0.a AND x0.a <= 3
```

---

## Numeric Typing

Arithmetic operators require numeric operands.

Initial numeric types:

```text
INT
FLOAT
```

Expected promotion rule:

```text
INT operation INT     → INT, except division
INT operation FLOAT   → FLOAT
FLOAT operation INT   → FLOAT
FLOAT operation FLOAT → FLOAT
division              → numeric real-compatible result
```

The semantic layer rejects arithmetic involving incompatible types:

```forml
x0.segment + 1
x0.enabled * 2
```

Ordering comparisons require compatible ordered types. Equality and inequality require compatible scalar types but do not require numeric operands.

---

## Initial Affine Verification Profile

The AST and IR represent arithmetic structurally, but the first end-to-end verification profile is intentionally affine.

Supported initially:

```forml
x0.a + x0.b
x0.a - x0.b
-x0.a
2 * x0.a
x0.a * 2
x0.a / 2
2 * target - x0.a
```

Rules:

- multiplication has at least one compile-time numeric constant operand, including a numeric specification constant;
- division has a non-zero compile-time numeric constant denominator, including a numeric specification constant;
- symbolic products such as `x0.a * x0.b` are outside the initial profile;
- symbolic denominators such as `x0.a / x0.b` are outside the initial profile.

Unsupported forms must produce a precise capability diagnostic rather than being silently approximated.

A constant zero denominator is always a semantic error:

```forml
x0.a / 0
```

---

## Arithmetic in Assertions

Arithmetic expressions may appear on either side of a comparison:

```forml
x0.a + x0.b <= 7
2 * target >= x0.a - 1
0 <= target - x0.baseline
```

Boolean operators combine complete predicates:

```forml
x0.a + x0.b <= 7 AND target - x0.baseline >= 0
```

This is invalid because a numeric expression is not itself a predicate:

```forml
x0.a + x0.b AND target <= 7
```

---

## Arithmetic in Domain Bounds

Numeric interval bounds may be arithmetic expressions:

```forml
tolerance := 1.0
minimum_b := 0.0
maximum_b := 10.0

with domain(
    x0.a: [x0.b - tolerance, x0.b + tolerance],
    x0.b: [minimum_b, maximum_b]
)
```

Normative rules:

1. Every input-feature reference in a domain is explicitly qualified; bare specification constants are allowed.
2. Referenced entities must be declared by the enclosing scope.
3. `target` is not allowed in a domain bound.
4. Bounds are simultaneous logical constraints, not assignments evaluated top to bottom.
5. Finite-set members remain literals in this patch.
6. Open and closed boundary semantics are preserved independently of bound expressions.

The example lowers conceptually to:

```text
x0.a >= x0.b - 1.0
AND x0.a <= x0.b + 1.0
AND x0.b >= 0.0
AND x0.b <= 10.0
```

Mutually dependent constraints are allowed because the domain is a conjunction, not an imperative computation.

---

## Binding Rules

In assertions, bare names resolve first to specification constants and then to implicit features:

```forml
offset := 1

[LOGIC]: forall x0 => a + offset <= target
```

`offset` resolves to the specification constant, while `a` resolves to `x0.a` because `x0` is the default entity.

In domains, references remain explicit:

```forml
with domain(
    x0.a: [x0.b - 1, x0.b + 1]
)
```

The following is rejected when `b` is not a specification constant:

```forml
with domain(
    x0.a: [b - 1, b + 1]
)
```

A bare specification constant is valid:

```forml
tolerance := 1

with domain(
    x0.a: [x0.b - tolerance, x0.b + tolerance]
)
```

A mismatched entity is also rejected.

---

## Target Reference Rules

`target` is a scalar-expression leaf representing the model output declared in the header.

It may appear alone or inside arithmetic assertions, on either side of a comparison:

```forml
target <= 7
target - x0.baseline <= 2
2 * target >= x0.a + x0.b
```

It may not appear in an input domain.

---

## AST Target Shape

```text
ScalarExpressionNode
├── ConstantNode
├── AttributeNode
├── TargetRefNode
├── UnaryArithmeticNode
│   ├── operator
│   └── operand: ScalarExpressionNode
└── BinaryArithmeticNode
    ├── left: ScalarExpressionNode
    ├── operator
    └── right: ScalarExpressionNode
```

Comparison becomes:

```text
ComparisonNode(
    left=ScalarExpressionNode,
    op=EnumComparisonOperator,
    right=ScalarExpressionNode,
)
```

Recommended canonical enums:

```text
EnumArithmeticOperator.ADD
EnumArithmeticOperator.SUB
EnumArithmeticOperator.MUL
EnumArithmeticOperator.DIV
EnumUnaryArithmeticOperator.POS
EnumUnaryArithmeticOperator.NEG
```

No solver object belongs in these AST nodes.

---

## IR Target Shape

IR1 preserves a backend-independent arithmetic tree:

```text
ScalarIR
├── ConstantIR
├── FeatureRefIR
├── ModelOutputRefIR
├── UnaryArithmeticIR
└── BinaryArithmeticIR
```

and:

```text
ComparisonIR(
    left: ScalarIR,
    op: EnumComparisonOperator,
    right: ScalarIR,
)
```

Logical normalization treats `ComparisonIR` as one atomic predicate. NNF, CNF, and DNF passes do not distribute through arithmetic subexpressions.

A later analysis may canonicalize eligible expressions into affine form, but user-authored arithmetic and model-generated assumptions retain distinct provenance.

---

## Failure Boundaries

| Failure | Expected boundary |
|---|---|
| malformed operator sequence | parser |
| chained comparison | parser or AST contract |
| numeric expression used as boolean | parser or semantic logic validation |
| unbound explicit feature | semantic binding |
| non-numeric arithmetic operand | semantic type validation |
| `target` used in a domain | semantic domain validation |
| division by literal zero | semantic arithmetic validation |
| unsupported nonlinear requirement | requirements/capability routing |
| backend cannot encode a valid expression | backend compilation |

---

## Required Golden Cases

Valid:

```forml
x0.a + x0.b <= 7
2 * x0.a - 3 * x0.b >= target
-(x0.a - x0.b) <= 1
x0.a / 2 <= target
x0.a: [x0.b - 1, x0.b + 1]
```

Invalid or unsupported:

```forml
0 <= x0.a <= 3
x0.segment + 1 <= 2
x0.a / 0 <= 1
x0.a: [target - 1, target + 1]
x0.a * x0.b <= 5
```

---

## Related Documents

- [Assertions](assertions.md)
- [Domains](domains.md)
- [Grammar](grammar.md)
- [Syntax](syntax.md)
- [AST Contract](../contracts/ast-contract.md)
- [AST to Semantic Contract](../contracts/ast-to-semantic.md)
- [Semantic to IR1 Contract](../contracts/semantic-to-ir1.md)
- [Z3 Backend](../backends/z3.md)
