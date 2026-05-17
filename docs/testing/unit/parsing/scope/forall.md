
---

# 📄 `forall.md`

```md id="5p7br3"
# FORALL Scope

## Purpose

The `FORALL` scope defines universal quantification
over a domain or dataset.

---

## Supported structure

A `FORALL` scope may contain:

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
| Quantifier required     | FORALL must define a quantifier |
| Stable quantifier value | Quantifier must equal `forall`  |
| Domain optional         | Domain may be omitted           |

## Valid cases
minimal FORALL
FORALL with domain
## Invalid cases

[TO_VERIFY]

## Tested by
| Test File        |
| ---------------- |
| `test_forall.py` |
