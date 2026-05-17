# Body Parsing

## Purpose

The body contains FORML properties and assertions.

---

## Supported structure

The body currently supports:

- one or more properties
- assertions
- optional backend attachment

---

## Responsibilities

The body is responsible for:

- grouping properties
- preserving property order
- validating property structure

---

## Core invariants

| Invariant | Description |
|---|---|
| Property required | Body must contain properties |
| Assertion required | Properties require assertions |
| Stable property ordering | Property order must be preserved |
| Explicit rejection | Invalid body structures must fail |

---

## Valid cases

- single property body
- body with backend
- multiple properties

---

## Invalid cases

- empty body
- malformed assertion
- invalid body syntax
- multiple expressions [TO_VERIFY]

---

## Tested by

| Test Files |
|---|
| `test_body.py` |
| `test_semantic.py` |