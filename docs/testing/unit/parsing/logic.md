# Logic Parsing Tests

## Scope

These tests validate logical expressions inside assertions.

---

## Supported operators

- AND
- OR
- NOT
- IMPLICATION

---

## Objectives

Ensure:

- correct AST construction
- correct operator precedence
- correct parentheses handling
- correct nesting behavior

---

## Precedence rules

From highest to lowest:

1. NOT
2. AND
3. OR
4. IMPLICATION

---

## Invariants

- NOT applies to a single operand
- AND/OR are n-ary nodes
- IMPLICATION is binary
- parentheses override precedence

---

## Invalid cases

- malformed expressions
- invalid parentheses
- incomplete expressions