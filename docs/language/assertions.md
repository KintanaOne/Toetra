# Assertions

> Status: Implemented / stabilizing  
> Scope: RHS logical expressions  
> Priority: P1  
> Audience: DSL users, IR authors, backend authors, test authors

## Purpose

Assertions define what must hold within a property scope.

They are the right-hand side of a property rule:

```forml
[PROPERTY]: scope => assertion
```

Assertions are compiled into logical AST nodes, then into IR logical nodes, then normalized through IR1 and IR2.

---

## Assertion Categories

FORML assertions currently include:

| Category | Example | Purpose |
|---|---|---|
| Comparison | `score >= 0` | Atomic predicate. |
| Boolean composition | `a >= 0 AND b <= 1` | Combine predicates. |
| Negation | `NOT age < 18` | Express logical negation. |
| Implication | `age >= 18 -> score >= 0.5` | Conditional property. |
| Parentheses | `(a AND b) OR c` | Control precedence. |
| Problem predicate | `CLASSIFICATION.EQUAL()` | ML task-level semantic predicate. |

---

## Comparison Assertions

Comparison assertions are atomic predicates.

Examples:

```forml
score >= 0
score <= 1
age == 42
segment != "A"
```

Conceptual AST:

```text
ComparisonNode(
  left=AttributeNode(...),
  op=EnumComparisonOperator,
  right=ConstantNode(...)
)
```

Conceptual IR:

```text
ComparisonIR(
  entity="x'",
  feature="score",
  op=GTE,
  value=0
)
```

The entity should come from semantic resolution, not raw syntax alone.

---

## Attribute References

Attributes can be explicit:

```forml
x.age >= 18
x'.score <= 1
```

or implicit:

```forml
age >= 18
```

Implicit attributes are resolved by the semantic context.

Example in an `at x` scope:

```forml
[BOUND]: at x in neighborhood(metric=L2, eps=0.1) => age >= 18
```

The semantic layer resolves:

```text
age → x'.age
```

---

## Boolean Composition

Assertions may be combined with boolean operators.

### AND

```forml
score >= 0 AND score <= 1
```

Meaning:

```text
Both predicates must hold.
```

### OR

```forml
segment == "A" OR segment == "B"
```

Meaning:

```text
At least one predicate must hold.
```

### NOT

```forml
NOT score < 0
```

Meaning:

```text
The predicate must not hold.
```

### Implication

```forml
age >= 18 -> score >= 0.5
```

Meaning:

```text
If age is at least 18, then score must be at least 0.5.
```

---

## Operator Precedence

The intended precedence is:

```text
parentheses
NOT
AND
OR
IMPLY
```

Implication is right-associative:

```forml
a -> b -> c
```

should be interpreted as:

```text
a -> (b -> c)
```

unless explicitly parenthesized differently.

---

## Problem Predicates

Problem predicates express ML task-level conditions.

Examples:

```forml
CLASSIFICATION.EQUAL()
REGRESSION.BETWEEN()
```

They are represented as semantic logical leaves:

```text
ProblemIR(problem=CLASSIFICATION, function=EQUAL)
```

Problem predicates require compatibility validation:

- problem/function compatibility,
- model task compatibility,
- property compatibility,
- backend support.

---

## IR1 Normalization

IR1-NNF is the planned early logical normalization subphase.

It should handle:

- implication elimination or normalization,
- De Morgan transformations,
- pushing negations inward,
- producing NNF where applicable.

Example:

```forml
NOT (age < 18 OR score < 0)
```

NNF form:

```text
NOT age < 18 AND NOT score < 0
```

Depending on the chosen representation, comparison negation may later be normalized into inverted comparison operators.

---

## IR2 Normal Forms

IR2 is planned for clause-oriented forms.

It may produce:

| Form | Use Case |
|---|---|
| CNF | Solver-style conjunction of clauses. |
| DNF | Scenario exploration and case splitting. |

IR2 should define whether transformations preserve:

- strict logical equivalence,
- equisatisfiability,
- or a traced approximation.

---

## Assertion Aggregation

Assertions are not lowered alone in the target architecture.

They are combined with:

- scope constraints,
- semantic constraints,
- ModelBridge-derived constraints,
- backend capability constraints.

The output is an `AggregatedAssertionSet`, then a `LoweredQuery`, then a backend-specific query.

---

## Known Stabilization Items

| Item | Issue | Recommended Fix |
|---|---|---|
| Logic operator casing | Lowercase tokens vs uppercase literals. | Normalize consistently. |
| `logic_expr` overlap | Attribute logical operation value is ambiguous. | Prefer `comparison_expr` as atomic predicate. |
| Problem/function validation | Raw strings and enums can be mixed. | Normalize before validation. |
| IR comparison entity | Raw `AttributeNode.entity` may be missing. | Use semantic resolved entity/path. |
| Pretty printer | Must display actual operator. | Use `ComparisonIR.op`. |

---

## Testing Requirements

Assertions need tests for:

- atomic comparisons,
- nested boolean expressions,
- operator precedence,
- parentheses,
- negation,
- implication,
- problem predicates,
- NNF transformations,
- CNF/DNF transformations,
- Hypothesis-generated logical trees,
- intelligent fuzzing of ambiguous expressions,
- Miova mutations on AST and IR logical nodes.

---

## Related Documents

- [Grammar](grammar.md)
- [Syntax](syntax.md)
- [IR1 NNF](../ir/ir1-nnf.md)
- [IR2 Normal Forms](../ir/ir2-normal-forms.md)
- [Semantic to IR1 Contract](../contracts/semantic-to-ir1.md)
