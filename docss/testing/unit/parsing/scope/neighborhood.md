
# Neighborhood Parsing

## Purpose

Neighborhoods define local perturbation constraints
used in robustness scopes.

---

## Supported components

A neighborhood contains:

- a metric
- arguments

---

## Example structure

```text
in neighborhood(L2,eps=0.01)
```

## Core invariants
| Invariant               | Description                           |
| ----------------------- | ------------------------------------- |
| Metric required         | Neighborhood must define a metric     |
| Arguments valid         | Arguments must be syntactically valid |
| Stable argument mapping | Arguments preserve key/value pairs    |

## Shared usage

Neighborhoods are used by:

- AT
- PAIRWISE
## Tested by
| Test Files         |
| ------------------ |
| `test_at.py`       |
| `test_pairwise.py` |
| `test_body.py`     |
| `test_semantic.py` |
