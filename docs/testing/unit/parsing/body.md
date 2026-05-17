# Body Parsing Tests

## Scope

These tests validate the body section of a FORML program.

The body contains one or more properties.

---

## Responsibilities

- ensure body is not empty (when required)
- validate property parsing
- validate backend attachment
- validate assertion structure

---

## Valid cases

- single property programs
- programs with backend attached
- simple assertion bodies

---

## Invalid cases

- empty body
- malformed assertion
- syntactic errors in body

---

## Invariant

```text
A program must contain at least one valid property in its body.
```