
# Program Structure

## Purpose

A FORML program defines the top-level structure parsed by the parser
and transformed into an AST program.

---

## Supported structure

A program may contain:

- a header
- a body
- [TO_VERIFY] footer

---

## AST mapping

Parsed into:

`ProgramNode`

## Core invariants
| Invariant         | Description                                 |
| ----------------- | ------------------------------------------- |
| Header required   | Programs require a valid header             |
| Body required     | Programs require properties                 |
| Stable ordering   | Header must appear before body              |
| Stable AST typing | Programs must map to a stable AST structure |

## Responsibilities

Programs are responsible for:

- defining global configuration
- grouping properties
- preserving parsing consistency
## Tested by
| Test Files         |
| ------------------ |
| `test_header.py`   |
| `test_body.py`     |
| `test_semantic.py` |
