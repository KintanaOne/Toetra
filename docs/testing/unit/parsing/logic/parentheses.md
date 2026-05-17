
# Parentheses Handling

## Purpose

Parentheses allow explicit logical grouping
inside FORML assertions.

---

## Responsibilities

Parentheses handling is responsible for:

- overriding operator precedence
- preserving grouping semantics
- preventing ambiguous parsing

---

## Expected behavior

Example:

```text
(A OR B) AND C
```
must preserve the grouped OR expression.

## Core invariants
| Invariant                       | Description                                      |
| ------------------------------- | ------------------------------------------------ |
| Parentheses override precedence | Grouped expressions must remain grouped          |
| Stable grouping                 | AST grouping must preserve parentheses semantics |
| Explicit rejection              | Invalid parentheses must fail parsing            |

## Invalid cases
- malformed parentheses
- incomplete grouped expressions

## Tested by
| Test Cases                                   |
| -------------------------------------------- |
| `test_logic_parentheses_override_precedence` |
| `test_invalid_parentheses`                   |
