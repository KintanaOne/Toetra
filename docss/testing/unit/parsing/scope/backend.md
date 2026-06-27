# Backend Attachment

## Purpose

Backends define optional execution or verification targets
attached to properties.

---

## Supported structure

A backend contains:

- a backend name
- optional arguments

---

## Example structure

```text
USING Z3
USING eran(param1="a")
```

## Core invariants
| Invariant               | Description                        |
| ----------------------- | ---------------------------------- |
| Backend optional        | Properties may omit backend        |
| Backend name required   | Backend must define a name         |
| Stable argument mapping | Arguments preserve key/value pairs |

## Backends are used by:

- PAIRWISE
- BODY
- SEMANTIC TESTS
## Tested by
| Test Files         |
| ------------------ |
| `test_pairwise.py` |
| `test_body.py`     |
| `test_semantic.py` |
