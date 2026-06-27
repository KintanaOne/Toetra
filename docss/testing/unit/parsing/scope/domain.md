# Domain Parsing

## Purpose

Domains restrict scope evaluation to specific value sets.

---

## Supported structure

A domain contains:

- a domain name
- a list of values

---

## Example structure

```text
with gender("male","female")
```

## Core invariants
| Invariant            | Description                       |
| -------------------- | --------------------------------- |
| Domain name required | Domain must define a name         |
| Values required      | Domain must contain values        |
| Stable ordering      | Values preserve declaration order |

## Domains are used by:

- AT
- FORALL
- EXISTS

## Tested by
| Test Files         |
| ------------------ |
| `test_at.py`       |
| `test_forall.py`   |
| `test_exists.py`   |
| `test_semantic.py` |
