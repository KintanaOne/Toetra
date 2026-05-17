
---

# 📄 `exists.md`

```md id="iwdldl"
# EXISTS Scope

## Purpose

The `EXISTS` scope defines existential quantification
over a domain or dataset.

---

## Supported structure

An `EXISTS` scope may contain:

- a quantifier
- an optional domain

---

## AST mapping

Parsed into:

```text
QuantifierExprNode
```

## Core invariants
| Invariant               | Description                     |
| ----------------------- | ------------------------------- |
| Quantifier required     | EXISTS must define a quantifier |
| Stable quantifier value | Quantifier must equal `exists`  |
| Domain optional         | Domain may be omitted           |

## Valid cases
- minimal EXISTS
- EXISTS with domain
## Invalid cases

[TO_VERIFY]

## Tested by
| Test File        |
| ---------------- |
| `test_exists.py` |
