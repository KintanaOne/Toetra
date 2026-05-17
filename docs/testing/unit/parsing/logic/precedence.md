# Operator Precedence

## Purpose

Logical operators must preserve deterministic precedence rules
during parsing and AST construction.

---

## Supported precedence

| Priority | Operator |
|---|---|
| Highest | NOT |
| Medium | AND |
| Low | OR |
| Lowest | IMPLICATION |

---

## Expected behavior

Examples:

```text
NOT A AND B
=> (NOT A) AND B
```
```text
A OR B AND C
=> A OR (B AND C)
```
```text
(A OR B) AND C
```

## Core invariants
| Invariant                       | Description                     |
| ------------------------------- | ------------------------------- |
| NOT precedence stable           | NOT binds before AND            |
| AND precedence stable           | AND binds before OR             |
| OR precedence stable            | OR binds before implication     |
| Parentheses override precedence | Explicit grouping must dominate |

## Tested by
| Test Cases                                   |
| -------------------------------------------- |
| `test_logic_operator_precedence`             |
| `test_logic_parentheses_override_precedence` |
| `test_logic_not_precedence`                  |
