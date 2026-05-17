# Property Structure

## Purpose

Properties define the main verification units inside a FORML program.

---

## Supported structure

A property currently contains:

- a property type
- a scope
- an assertion
- an optional backend

---

## Responsibilities

Properties are responsible for:

- defining verification contexts
- binding assertions to scopes
- attaching optional backends

---

## Core invariants

| Invariant | Description |
|---|---|
| Scope required | Properties require exactly one scope |
| Assertion required | Properties require assertions |
| Stable AST structure | Properties must map to stable AST nodes |
| Backend optional | Backend attachment may be omitted |

---

## Shared concepts

Properties interact with:

- scopes
- assertions
- backends
- semantic validation

---

## Tested by

| Test Files |
|---|
| `test_body.py` |
| `test_semantic.py` |
| `test_logic.py` |
| `test_pairwise.py` |
| `test_at.py` |
| `test_check_at.py` |
| `test_forall.py` |
| `test_exists.py` |