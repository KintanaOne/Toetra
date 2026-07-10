# Vocabulary

> Status: Implemented / needs normalization  
> Scope: Official FORML language vocabulary  
> Priority: P1  
> Audience: DSL users, compiler contributors, semantic layer maintainers

## Purpose

The vocabulary defines the official words, categories, enums, and symbolic values accepted by the FORML language.

It acts as a bridge between:

```text
DSL tokens
→ AST enum values
→ semantic compatibility rules
→ IR artifacts
→ backend lowering
```

Vocabulary normalization is critical because mismatches between raw strings, grammar token names, enum names, and enum values can create fragile compiler behavior.

---

## Property Types

Property types describe what kind of behavioral guarantee is being expressed.

| Property | Meaning | Current Status |
|---|---|---|
| `ROBUSTNESS` | Stability under perturbation or neighborhood changes. | implemented |
| `STABILITY` | Output or behavior stability under controlled conditions. | implemented |
| `FAIRNESS` | Pairwise or group-aware behavioral constraints. | implemented |
| `MONOTONICITY` | Output behavior should evolve monotonically with some feature or condition. | implemented |
| `BOUND` | Value or output must remain within a bound. | implemented |
| `LOGIC` | General logical property. | grammar-level support |

Property types are later checked against scope compatibility rules.

Example:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

---

## Problem Types

Problem types describe the ML task or semantic problem being referenced by a property.

| Problem | Meaning | Current Status |
|---|---|---|
| `CLASSIFICATION` | Classification task. | implemented |
| `PREDICTION` | Generic prediction task. | grammar-level support |
| `REGRESSION` | Regression task. | implemented |
| `CLUSTERING` | Clustering task. | partial semantic support |
| `ANOMALY_DETECTION` | Anomaly detection task. | grammar-level support |
| `REINFORCEMENT_LEARNING` | RL task. | grammar-level support |

Problem types appear in problem-level predicates:

```forml
CLASSIFICATION.EQUAL()
REGRESSION.BETWEEN()
```

---

## Functions

Functions describe semantic operations attached to problem predicates.

| Function | Example | Intended Meaning |
|---|---|---|
| `EQUAL` | `CLASSIFICATION.EQUAL()` | Equality or output preservation. |
| `EQUITY` | `CLASSIFICATION.EQUITY()` | Equity/fairness-oriented equality. |
| `BETWEEN` | `REGRESSION.BETWEEN()` | Output lies in an interval. |
| `INCREASING` | `REGRESSION.INCREASING()` | Monotonic increase. |
| `DECREASING` | `REGRESSION.DECREASING()` | Monotonic decrease. |

Function compatibility depends on the problem type.

For example:

| Problem | Compatible Functions |
|---|---|
| `CLASSIFICATION` | `EQUAL`, `EQUITY`, `BETWEEN` |
| `REGRESSION` | `EQUAL`, `INCREASING`, `DECREASING`, `BETWEEN` |
| `CLUSTERING` | currently empty / to define |

---

## Scopes and Quantifiers

FORML supports multiple ways to define where a property is evaluated.

| Vocabulary | Example | Semantic Scope |
|---|---|---|
| `at` | `at x` | local |
| `check_at` | `check_at x` | pointwise |
| pairwise token | `x ~ x'` | pairwise |
| `forall` / `∀` | `forall x0 with domain(...)` | quantifier |
| `exists` / `∃` | `exists x0 with domain(...)` | quantifier |

Quantifier tokens should be normalized before semantic validation.

Recommended internal normalized values:

```text
forall
exists
```

Accepted user-facing forms include a mandatory identifier:

```text
forall x0
exists x0
∀ x0
∃ x0
```

The tokens normalize to `forall` or `exists`, while the declared identifier remains a separate preserved binding. See [Quantified Variable Bindings](quantified-bindings.md).

---

## Domain Vocabulary

| Vocabulary | Example | Meaning |
|---|---|---|
| `with domain` | `with domain(x0.age: [18, 65])` | Introduces input admissibility constraints. |
| `[` on lower side | `[0, 1]` | Closed lower boundary. |
| `]` on lower side | `]0, 1]` | Open lower boundary. |
| `]` on upper side | `[0, 1]` | Closed upper boundary. |
| `[` on upper side | `[0, 1[` | Open upper boundary. |
| `{...}` | `{EU, US}` | Finite discrete set. |
| symbolic literal | `EU` | Unquoted categorical value inside a finite set. |

Recommended canonical internal values:

```text
EnumBoundaryKind.OPEN
EnumBoundaryKind.CLOSED
```

The same bracket glyph has a different role depending on whether it appears on the lower or upper side. The AST must preserve the resulting boundary kind rather than relying on raw characters downstream.

`domain` should be reserved as a keyword. Unquoted identifiers inside finite sets should be represented as symbolic literals, not input-variable references.

---

## Metrics

Metrics define perturbation neighborhoods.

| Metric | Example | Meaning |
|---|---|---|
| `L1` | `metric=L1` | Manhattan distance. |
| `L2` | `metric=L2` | Euclidean distance. |
| `Linf` | `metric=Linf` | Infinity norm. |

Example:

```forml
at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

Metric values should be normalized so that grammar strings, enum values, and semantic values are consistent.

---

## Logical Operators

Logical operators compose assertions.

| Operator | Meaning | Recommended Canonical Form |
|---|---|---|
| `AND` | conjunction | `AND` |
| `OR` | disjunction | `OR` |
| `NOT` | negation | `NOT` |
| `->` | implication | `IMPLY` internally |

The language may choose to accept lowercase forms, but internal representation should normalize operators.

---

## Comparison Operators

Comparison operators define atomic predicates.

| Operator | Meaning |
|---|---|
| `==` | equal |
| `!=` | not equal |
| `<` | less than |
| `<=` | less than or equal |
| `>` | greater than |
| `>=` | greater than or equal |

Example:

```forml
age >= 18
score <= 1.0
```

---

## Arithmetic Operators

| Operator | Canonical enum intent | Meaning |
|---|---|---|
| `+` | `ADD` or unary `POS` | Addition or unary identity. |
| `-` | `SUB` or unary `NEG` | Subtraction or unary negation. |
| `*` | `MUL` | Multiplication. |
| `/` | `DIV` | Division. |

Recommended internal vocabularies:

```text
EnumArithmeticOperator.ADD
EnumArithmeticOperator.SUB
EnumArithmeticOperator.MUL
EnumArithmeticOperator.DIV
EnumUnaryArithmeticOperator.POS
EnumUnaryArithmeticOperator.NEG
```

The same surface token may have unary or binary meaning according to CST position. The builder must normalize it into the corresponding canonical enum.

The initial verification profile permits only affine multiplication/division shapes. This is a capability rule, not a token-normalization rule.

## Backends

Current grammar-level backend names include:

| Backend | Status |
|---|---|
| `z3` / `Z3` | planned critical backend |
| `eran` / `ERAN` | planned backend |
| `zonotope` / `ZONOTOPE` | planned abstraction/backend mode |
| `box` / `BOX` | planned abstraction/backend mode |

Backends should be normalized at the AST or semantic boundary.

Recommended internal representation:

```text
EnumBackend.Z3
EnumBackend.ERAN
EnumBackend.ZONOTOPE
EnumBackend.BOX
```

---

## Normalization Rules

The vocabulary layer should converge toward a single rule:

```text
User-facing strings may be flexible.
Internal compiler values must be canonical.
```

Recommended canonicalization boundaries:

| Boundary | Responsibility |
|---|---|
| Parser | Preserve syntactic tokens. |
| Builder | Convert tokens into AST values and enums. |
| Semantic validation | Normalize and validate compatibility. |
| IR translation | Consume canonical enum values only. |
| Backend lowering | Consume backend-safe normalized values only. |

---

## Known Stabilization Items

| Item | Issue | Recommended Fix |
|---|---|---|
| Quantifier vocabulary | Token names and enum values may diverge. | Normalize to `forall` / `exists`. |
| Metric enum values | Quoted values can leak into enum values. | Store clean values such as `L1`, `L2`, `Linf`. |
| Backend enum names | Mixed lowercase/uppercase enum members. | Use canonical uppercase enum names. |
| Logical casing | Lowercase tokens vs uppercase grammar literals. | Accept flexible syntax, normalize internally. |
| Problem/function validation | Must compare enums, not raw strings. | Use a shared enum normalization helper. |
| Arithmetic operators | Unary and binary tokens reuse `+` and `-`. | Normalize by AST role into explicit unary/binary enums. |

---

## Related Documents

- [Grammar](grammar.md)
- [Syntax](syntax.md)
- [Properties](properties.md)
- [Assertions](assertions.md)
- [Arithmetic Expressions](arithmetic-expressions.md)
- [Backends Syntax](backends.md)
