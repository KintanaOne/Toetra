
# CHECK_AT Scope

## Purpose

The `CHECK_AT` scope validates assertions
against a single explicit point.

---

## Supported structure

A `CHECK_AT` scope contains:

- a variable
- an assertion

---

## Example structure

```text
CHECK_AT x0
```

## AST mapping

Parsed into:

`CheckAtExprNode`
## Core invariants
| Invariant          | Description                  |
| ------------------ | ---------------------------- |
| Variable required  | CHECK_AT requires a variable |
| Assertion required | Assertion cannot be empty    |
| Stable AST typing  | Must produce CheckAtExprNode |

## Valid cases
- minimal CHECK_AT
- CHECK_AT with complex assertion
## Invalid cases
- missing identifier
- missing assertion
- invalid identifier
## Tested by
| Test File          |
| ------------------ |
| `test_check_at.py` |
