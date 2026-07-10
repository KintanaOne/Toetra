# IR1 NNF

> Status: Implemented / Stabilizing  
> Implementation: Early logical normalization with De Morgan and Negation Normal Form  
> Scope: First normalized logical representation

## Purpose

IR1 is FORML's first backend-independent logical representation.

Its role is not only to represent a property as a `VerificationTask`, but also to begin logical normalization.

IR1 should make the logical query easier to reason about, transform, test, and prepare for IR2.

---

## IR1 Responsibilities

IR1 is responsible for:

- representing one property as a verification task,
- projecting semantic scope into `ScopeIR`,
- representing RHS assertions as Logical IR,
- flattening simple boolean structures where appropriate,
- eliminating or preparing implications,
- applying De Morgan transformations,
- producing or enforcing Negation Normal Form.

---

## Negation Normal Form

A logical expression is in Negation Normal Form, or NNF, when negation appears only directly in front of atomic predicates.

Examples:

```text
NOT(A AND B)
```

becomes:

```text
NOT(A) OR NOT(B)
```

And:

```text
NOT(A OR B)
```

becomes:

```text
NOT(A) AND NOT(B)
```

---

## De Morgan Transformations

IR1 uses De Morgan transformations to push negations inward.

| Input | Output |
|---|---|
| `NOT(A AND B)` | `NOT(A) OR NOT(B)` |
| `NOT(A OR B)` | `NOT(A) AND NOT(B)` |
| `NOT(NOT(A))` | `A` |

These transformations preserve logical equivalence.

---

## Implication Handling

Implication should not remain as an unnormalized backend concern unless a backend explicitly supports it.

The standard transformation is:

```text
A -> B
```

becomes:

```text
NOT(A) OR B
```

Then NNF rules are applied.

---

## IR1 Output Contract

A valid IR1-NNF query should satisfy:

| Invariant | Description |
|---|---|
| Backend-independent | No solver-specific encoding. |
| Semantically resolved | Attributes should reference resolved entities. |
| No raw DSL syntax | Source syntax should not leak into IR1. |
| Explicit logical structure | Boolean operators are represented structurally. |
| Negation normalized | Negation is pushed toward leaves. |
| Implication handled | Implication is eliminated or explicitly marked for later handling. |
| Traceable | Nodes should remain traceable to the originating assertion where possible. |

---

## Arithmetic Atom Invariant

A comparison remains an atomic logical predicate even when its operands contain arithmetic.

Example:

```text
ComparisonIR(
    left=ADD(FeatureRef(x0.a), MUL(Constant(2), FeatureRef(x0.b))),
    op=LTE,
    right=ModelOutputRef(MyTarget),
)
```

NNF may move a negation onto this comparison or invert its comparison operator. It must not apply De Morgan or distributive laws inside the scalar-expression tree.

Therefore:

```forml
NOT (x0.a + 2 * x0.b <= target)
```

is one negated atom, not a boolean expression over `x0.a`, `x0.b`, and `target`.

## What IR1 Does Not Do

IR1 does not select the final solver form.

It should not perform:

- CNF conversion,
- DNF conversion,
- backend-specific encoding,
- model constraint aggregation,
- solver-specific simplification,
- Z3 expression construction.

These belong to later layers.

---

## IR1 vs IR2

| Layer | Role |
|---|---|
| IR1 | Normalize logical structure and negation. |
| IR2 | Produce clause-oriented or case-oriented normal forms. |

IR1 prepares the expression.  
IR2 chooses the form needed by the verification strategy.

---

## Example

Input DSL assertion:

```forml
NOT(age <= 30 AND score >= 0.8)
```

Initial Logical IR:

```text
NotIR(
  AndIR([
    ComparisonIR(age <= 30),
    ComparisonIR(score >= 0.8)
  ])
)
```

IR1-NNF:

```text
OrIR([
  NotIR(ComparisonIR(age <= 30)),
  NotIR(ComparisonIR(score >= 0.8))
])
```

A later simplification layer may invert comparison operators:

```text
age > 30 OR score < 0.8
```

That comparison inversion can be implemented either in IR1 normalization or in a later simplification pass, but the boundary must be explicit.

---

## Relationship with Testing

IR1-NNF requires golden tests.

Examples should cover:

- double negation,
- nested AND/OR negations,
- implications,
- parentheses precedence,
- problem predicates under negation,
- mixed comparisons and problem predicates;
- arithmetic comparisons under negation;
- preservation of arithmetic tree shape during operator inversion.

---

## Relationship with Miova

Miova can test IR1 by generating or mutating logical trees around:

- invalid negation placement,
- equivalent De Morgan rewrites,
- implication rewrites,
- nested boolean structures,
- unsupported leaves under negation.

Expected outcomes should distinguish:

- valid equivalent rewrite,
- valid but non-normal form,
- rejected invalid structure,
- semantic mismatch.

---

## Summary

IR1-NNF is the first serious logical normalization layer in FORML.

It is where the system starts moving from “parsed property” to “formal logical object”.
