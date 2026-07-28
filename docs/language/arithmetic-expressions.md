# Arithmetic expressions

> Status: Accepted syntax and semantics; affine built-in V1 execution
> Scope: Numeric scalar expressions in assertions and interval bounds
> Audience: users, semantic contributors, and backend authors

## Expression model

A comparison relates two scalar expressions:

```text
scalar expression
comparison operator
scalar expression
```

Examples:

```toetra
applicant.revenue - applicant.cost >= 0
2 * applicant.income - applicant.debt <= target[applicant]
target[candidate] - target[baseline] <= tolerance
```

The compiler preserves operand order and grouping as a structured tree. It does
not flatten user arithmetic into text or backend-native expressions.

## Leaves

| Leaf | Example | Meaning |
|---|---|---|
| numeric literal | `3`, `0.5` | integer or real scalar |
| specification constant | `tolerance` | immutable header value |
| explicit feature | `applicant.income` | feature of one visible point |
| implicit feature | `income` | feature of the unique default point |
| regression output | `target[applicant]` | scalar model evaluation |
| class probability | `target[applicant].probability("yes")` | typed probability observable |
| parentheses | `(a + b)` | explicit grouping |

Booleans, strings, and predicted labels can participate in compatible equality
comparisons but not arithmetic.

## Operators and precedence

| Level | Operators | Associativity |
|---|---|---|
| strongest | parentheses | explicit |
| unary | `+`, `-` | right |
| multiplicative | `*`, `/` | left |
| additive | `+`, `-` | left |
| weakest scalar layer | comparisons | non-associative |

Therefore:

```toetra
a + 2 * b <= target
```

means:

```text
a + (2 * b) <= target
```

Chained comparisons do not parse. Write:

```toetra
0 <= applicant.score and applicant.score <= 1
```

## Numeric typing

Arithmetic operands must be numeric. With known schema types:

```text
INT op INT     → numeric
INT op FLOAT   → FLOAT-compatible
FLOAT op INT   → FLOAT-compatible
FLOAT op FLOAT → FLOAT-compatible
division       → real-compatible
```

Examples rejected by semantic typing:

```text
applicant.region + 1
target[applicant].label * 2
```

Ordering comparisons also require numeric operands. Equality and inequality
require compatible scalar types.

## Arithmetic classification

Semantic analysis classifies every numeric tree before backend selection:

| Class | Examples | Built-in V1 |
|---|---|---|
| affine | `a + b`, `2 * a`, `a / 2` | supported |
| nonlinear | `a * b` | capability-rejected |
| symbolic division | `a / b` | capability-rejected |

### Affine rules

The public built-in route supports:

- addition and subtraction;
- unary plus and minus;
- multiplication when at least one operand is a compile-time numeric constant;
- division by a non-zero compile-time numeric constant.

Specification constants count as compile-time constants after semantic
resolution.

### Constant division by zero

```text
a / 0
a / (1 - 1)
```

These are semantic errors. They do not reach capability routing.

### Unsupported arithmetic is preserved

For:

```toetra
applicant.income * applicant.debt <= target[applicant]
```

the language and semantic layers preserve a nonlinear requirement. The affine
Z3 route rejects it. Toetra must not replace it with a bound, sample, tangent,
or other approximation.

## Domain bounds

Arithmetic may appear in numeric interval bounds:

```toetra
tolerance := 1000.0

[LOGIC]:
forall baseline, candidate
with domain(
    baseline.income: [0.0, 100000.0],
    candidate.income: [
        baseline.income - tolerance,
        baseline.income + tolerance
    ]
)
=> target[candidate] <= target[baseline] + 0.02
```

Domain-specific rules still apply:

- every feature reference is explicitly point-qualified;
- bare names may resolve to specification constants, not implicit features;
- `target` and classification observables are prohibited in domain bounds;
- every bound must be numeric.

## Model output rules

Scalar regression outputs may participate in affine arithmetic:

```toetra
target[candidate] - target[baseline] <= 0.02
```

Predicted labels do not. Class probabilities are scalar observables, but the
public binary V1 route supports only direct order comparisons against thresholds
strictly inside `(0, 1)`; probability arithmetic is excluded by the public
profile.

## Logical normalization

A complete comparison is one logical atom:

```toetra
not (applicant.income + applicant.savings <= target[applicant])
```

NNF may negate or invert the comparison, but it does not distribute through,
reorder, or approximate the scalar tree.

## Current representations

The as-built path uses:

```text
ConstantNode / AttributeNode / TargetRefNode
UnaryArithmeticNode / BinaryArithmeticNode
→ scalar IR1 expression nodes
→ arithmetic requirements in IR2
→ capability-qualified backend translation
```

Backend expressions never appear in the AST or IR1.

## Failure ownership

| Failure | Boundary |
|---|---|
| malformed operator sequence or chained comparison | parser |
| unknown explicit point/feature | semantic binding/schema validation |
| non-numeric operand | semantic scalar typing |
| constant zero denominator | semantic scalar typing |
| nonlinear or symbolic-division requirement | route qualification |
| qualified expression cannot be translated | backend adapter |

## Related pages

- [Language support levels](support-levels.md)
- [Assertions](assertions.md)
- [Domains](domains.md)
- [Model output observables](model-output-observables.md)
- [Scalar-expression contract](../contracts/quantified-domain-scalar-expressions.md)
- [Backend capabilities](../backends/capabilities.md)
