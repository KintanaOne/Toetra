
---

# 📄 `pairwise.md`

```md id="jk2o0j"
# PAIRWISE Scope

## Purpose

The `PAIRWISE` scope compares two related inputs
inside a relational robustness context.

---

## Supported structure

A `PAIRWISE` scope contains:

- a pair of variables
- a neighborhood
- an optional backend
- an optional domain

---

## Example structure

```text
x ~ x'
```

## AST mapping

Parsed into:

`PairwiseExprNode`
## Core invariants
| Invariant                | Description                            |
| ------------------------ | -------------------------------------- |
| Two identifiers required | Pairwise requires x and x'             |
| Neighborhood required    | Pairwise requires a neighborhood       |
| Pair format stable       | Pair must preserve left/right ordering |
| Backend optional         | Backend may be omitted                 |

## Valid cases
- minimal pairwise
- pairwise with backend
## Invalid cases
- missing identifier
- missing prime identifier
- malformed pair
- malformed neighborhood
- missing assertion
## Tested by
| Test File          |
| ------------------ |
| `test_pairwise.py` |
