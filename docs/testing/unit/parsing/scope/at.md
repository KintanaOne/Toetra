# AT Scope

## Purpose

The `AT` scope defines a local robustness context
bound to a single variable.

---

## Supported structure

An `AT` scope may contain:

- a variable
- an optional neighborhood
- an optional domain

---

## Example structure

```text
AT x0
AT x0 IN L2(eps=0.01)
AT x0 WHERE sex IN ["male", "female"]
```

## AST mapping

Parsed into:

`AtExprNode`

## Core invariants
| Invariant                 | Description                          |
| ------------------------- | ------------------------------------ |
| Variable required         | AT scope requires a variable         |
| Neighborhood optional     | Neighborhood may be omitted          |
| Domain optional           | Domain may be omitted                |
| Valid neighborhood syntax | Neighborhood arguments must be valid |
| Valid domain syntax       | Domain values must be valid          |

## Valid cases
- minimal AT
- AT with neighborhood
- AT with domain
- AT with neighborhood and domain

## Invalid cases
- missing identifier
- malformed neighborhood
- malformed domain
- invalid neighborhood arguments

## Tested by
| Test File    |
| ------------ |
| `test_at.py` |
