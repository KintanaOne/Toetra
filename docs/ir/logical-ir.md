# Logical IR

> Status: Implemented / Stabilizing  
> Implementation: IR1 logical tree  
> Scope: Boolean and problem-level query representation

## Purpose

Logical IR represents the right-hand side of a FORML property as a structured logical tree.

It removes DSL syntax while preserving logical meaning.

Logical IR is used for:

- boolean reasoning,
- normalization,
- De Morgan transformations,
- NNF conversion,
- future CNF/DNF conversion,
- backend lowering,
- Miova mutation campaigns.

---

## Core Concepts

Logical IR is composed of:

| Node | Role |
|---|---|
| `ComparisonIR` | Atomic feature comparison. |
| `AndIR` | Conjunction of operands. |
| `OrIR` | Disjunction of operands. |
| `NotIR` | Negation of one operand. |
| `ImplyIR` | Logical implication. |
| `ProblemIR` | High-level ML problem predicate. |

---

## ComparisonIR

`ComparisonIR` represents atomic predicates.

Example:

```forml
age <= 30
```

Conceptual IR:

```text
ComparisonIR
├── entity = x'
├── feature = age
├── op = <=
└── value = 30
```

A comparison must use semantically resolved entity information whenever possible.

The raw parsed entity is not always sufficient because DSL syntax may allow implicit access:

```forml
age <= 30
```

In a local scope, this may resolve to:

```text
x'.age <= 30
```

---

## Boolean Operators

### AndIR

Represents conjunction.

```text
AND(A, B, C)
```

### OrIR

Represents disjunction.

```text
OR(A, B, C)
```

### NotIR

Represents negation.

```text
NOT(A)
```

In IR1-NNF, negation should eventually appear only in front of atomic predicates or supported leaves.

### ImplyIR

Represents implication.

```text
A -> B
```

Implications should be eliminated or normalized during IR1 normalization when producing NNF.

---

## ProblemIR

`ProblemIR` represents high-level ML problem predicates.

Examples:

```forml
CLASSIFICATION.EQUAL()
REGRESSION.BETWEEN()
```

Conceptual IR:

```text
ProblemIR
├── problem = CLASSIFICATION
├── function = EQUAL
└── args = {}
```

Problem-level predicates are not simple boolean comparisons. They require later interpretation using:

- model task,
- target information,
- prediction function,
- output semantics,
- backend capabilities.

---

## Logical IR Invariants

A valid Logical IR tree must satisfy:

| Invariant | Description |
|---|---|
| No CST leakage | Logical IR must not contain Lark trees or tokens. |
| No AST-only nodes | It should use IR nodes, not raw AST nodes. |
| Resolved attributes | Comparisons should rely on semantic resolution. |
| Typed operators | Comparison operators must use official operator enums. |
| Valid problem/function pair | ProblemIR must obey compatibility rules. |
| Structural validity | AND/OR nodes must have operands; NOT must have one operand. |

---

## Current Stabilization Points

The current Logical IR is a solid first structure, but must be hardened:

- comparison pretty-printing should display the real comparison operator;
- comparison translation should consume `SemanticAnnotations.resolved_entity` and `resolved_path`;
- problem/function conversion should handle enum values and strings consistently;
- implication should be normalized as part of IR1-NNF;
- logical operator casing should be normalized between grammar, AST builder, and IR.

---

## Relationship with IR1-NNF

Logical IR is the tree structure.

IR1-NNF is a normalization invariant applied to that structure.

```text
LogicalIR tree + normalization rules → IR1-NNF
```

---

## Relationship with IR2

IR2 consumes normalized Logical IR and transforms it into forms such as:

- CNF,
- DNF,
- backend-preparation normal forms.

---

## Relationship with Miova

Logical IR is one of the richest mutation surfaces.

Miova can mutate:

- operators,
- operands,
- negation placement,
- boolean structure,
- implication direction,
- comparison values,
- problem/function pairs.

This helps test whether FORML detects invalid logic, preserves valid semantics, and rejects unsupported transformations.

---

## Summary

Logical IR is the formal logical core of FORML.

It is where user assertions stop being DSL text and become structured reasoning artifacts.
