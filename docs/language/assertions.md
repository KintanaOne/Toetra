# Assertions

> Status: Target contract accepted for documentation-first implementation  
> Scope: RHS logical expressions  
> Priority: P0  
> Audience: DSL users, AST/IR authors, semantic validators, backend authors, test authors

## Purpose

Assertions define what must hold within a property scope:

```forml
[PROPERTY]: scope => assertion
```

They compile through logical CST, AST, semantic validation, IR1, IR2, and the final verification condition.

---

## Assertion Categories

| Category | Example | Purpose |
|---|---|---|
| Comparison | `target <= 7` | Atomic predicate. |
| Arithmetic comparison | `2 * x0.a + x0.b <= target` | Relate numeric expressions. |
| Boolean composition | `a >= 0 AND b <= 1` | Combine predicates. |
| Negation | `NOT age < 18` | Negate a predicate. |
| Logical implication | `age >= 18 -> target >= 0.5` | Conditional rule. |
| Parentheses | `(a >= 0 AND b <= 1) OR target == 0` | Control precedence. |
| Problem predicate | `forall baseline, candidate => CLASSIFICATION.EQUAL()` | Binary predicted-label equality sugar. |

---

## Atomic Comparisons

The normative comparison shape is:

```text
scalar_expression comparison_operator scalar_expression
```

Examples:

```forml
target >= 0
x0.age == 42
x0.segment != "A"
x0.a + x0.b <= 7
2 * target >= x0.a - 1
```

The previous restricted shape `attribute comparison_operator constant` is superseded.

Conceptual AST:

```text
ComparisonNode(
    left=ScalarExpressionNode(...),
    op=EnumComparisonOperator,
    right=ScalarExpressionNode(...),
)
```

Conceptual IR1:

```text
ComparisonIR(
    left=ScalarIR(...),
    op=EnumComparisonOperator,
    right=ScalarIR(...),
)
```

---

## Scalar Expressions

Comparison operands may contain literals, specification constants, explicit or implicit input features, `target`, unary arithmetic, binary arithmetic, and parentheses.

Arithmetic typing and profile restrictions are defined in [Arithmetic Expressions](arithmetic-expressions.md).

---

## Attribute and Target References

Input features can be explicit:

```forml
x0.age >= 18
```

or implicit:

```forml
age >= 18
```

Example:

```forml
[LOGIC]: forall x0 => age + 1 <= target
```

resolves conceptually to:

```text
x0.age + 1 <= _model.<declared-target>
```

`target` is a model-output reference, not an input feature.

---

## Specification-Constant References

Specification constants may appear anywhere a compatible scalar literal could appear:

```forml
max_risk := 0.20
max_ratio := 0.35

[LOGIC]:
forall applicant
    => target <= max_risk
       AND applicant.debt <= max_ratio * applicant.income
```

Bare-name resolution in assertions is:

1. matching specification constant;
2. otherwise implicit feature of the scope's default entity;
3. otherwise unbound-name error.

Explicit qualification bypasses this ambiguity:

```forml
threshold := 7

[LOGIC]: forall x0 => x0.threshold <= threshold
```

The left side denotes a feature; the right side denotes the specification constant. See [Specification Constants](specification-constants.md).

## Comparison Typing

| Operator family | Operand requirement |
|---|---|
| `<`, `<=`, `>`, `>=` | Compatible ordered scalar types; numeric in the initial profile. |
| `==`, `!=` | Compatible scalar types. |

Valid:

```forml
x0.a + 1 <= target
x0.segment == "A"
x0.enabled != false
```

Invalid:

```forml
x0.segment + 1 <= 2
x0.enabled < true
```

---

## Boolean Composition

Boolean operators compose complete predicates.

```forml
x0.a >= 0 AND x0.b <= 1
x0.segment == "A" OR x0.segment == "B"
NOT target < 0
x0.age >= 18 -> target >= 0.5
```

A scalar expression is not a predicate by itself:

```forml
x0.a + x0.b AND target <= 7
```

is invalid.

---

## Operator Precedence

From strongest to weakest:

```text
parenthesized scalar expression
unary arithmetic + and -
multiplication and division
addition and subtraction
comparison
NOT
AND
OR
logical implication
```

Logical implication is right-associative. Comparisons are non-associative, so chained comparisons are rejected.

---

## Problem Predicates

Problem predicates remain boolean leaves:

```forml
[ROBUSTNESS]: forall baseline, candidate => CLASSIFICATION.EQUAL()
REGRESSION.BETWEEN()
```

They cannot participate directly in arithmetic.

---

## Logical Normalization

A comparison containing arithmetic remains one atomic predicate. NNF, CNF, and DNF passes may negate or invert the comparison but do not distribute through its arithmetic tree.

Example:

```forml
NOT (x0.a + x0.b <= target OR target < 0)
```

NNF shape:

```text
NOT(x0.a + x0.b <= target)
AND
NOT(target < 0)
```

---

## Initial Verification Profile

The first end-to-end profile supports addition, subtraction, unary signs, multiplication by a numeric constant, and division by a non-zero numeric constant.

Nonlinear symbolic products and symbolic denominators require a stronger capability and must never be approximated silently.

---

## Failure Boundaries

| Failure | Expected boundary |
|---|---|
| malformed expression | parser |
| chained comparison | parser or AST contract |
| unbound explicit entity | semantic binding |
| incompatible arithmetic types | semantic type validation |
| division by zero constant | semantic arithmetic validation |
| unsupported nonlinear requirement | capability routing |
| backend encoding mismatch | backend compilation |

---

## Testing Requirements

Required tests include expression-to-expression comparisons, precedence, unary operators, implicit and explicit binding, type errors, division by zero, nonlinear capability rejection, logical normalization preservation, and Z3 translation of the affine profile.

---

## Related Documents

- [Arithmetic Expressions](arithmetic-expressions.md)
- [Grammar](grammar.md)
- [Syntax](syntax.md)
- [Domains](domains.md)
- [IR1 NNF](../ir/ir1-nnf.md)
- [Semantic to IR1 Contract](../contracts/semantic-to-ir1.md)
