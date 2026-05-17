
# Logic Parsing

## Purpose

FORML assertions support logical expressions
used to compose verification constraints.

---

## Supported operators

| Operator | Purpose |
|---|---|
| AND | Logical conjunction |
| OR | Logical disjunction |
| NOT | Logical negation |
| => | Logical implication |

---

## Supported node types

| AST Node |
|---|
| AndNode |
| OrNode |
| NotNode |
| ImplicationNode |
| ComparisonNode |
| ProblemNode |

---

## Responsibilities

Logic parsing is responsible for:

- preserving operator precedence
- preserving parentheses grouping
- constructing stable ASTs
- rejecting malformed logic

---

## Core invariants

| Invariant | Description |
|---|---|
| NOT unary | NOT must wrap a single operand |
| AND variadic | AND may contain multiple operands |
| OR variadic | OR may contain multiple operands |
| Implication binary | Implication requires left/right operands |
| Stable typing | Operators must map to stable AST nodes |

---

## Tested by

| Test File |
|---|
| `test_logic.py` |