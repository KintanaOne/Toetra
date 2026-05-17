# Header Parsing Tests

## Scope

These tests validate parsing and validation of the FORML program header.

The header defines:

- model path
- target variable

---

## Valid cases

Tests ensure that:

- header is always present
- model is a string path
- target is a valid identifier
- comments do not break parsing

---

## Invalid cases

The parser must reject:

- missing model
- missing target
- missing header fields
- invalid type for model
- invalid type for target

---

## Invariant

```text
A program is invalid if its header is incomplete or malformed.
```

## Covered files
test_header.py