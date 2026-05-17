# 📁 `docs/testing/unit/parsing/helpers.md`

# Parsing Test Helpers

## Purpose

This module provides reusable assertion utilities for parsing tests.

These helpers are NOT part of production code.
They exist to:

- reduce duplication in test assertions
- enforce consistent validation rules
- express AST expectations clearly

---

## Categories of helpers

### 1. Program construction

- `parse(code)` → raw Lark tree
- `build_program(code)` → full AST program
- `build_property(code)` → first property only

---

### 2. Structural assertions

- `assert_header`
- `assert_property_basics`
- `assert_scope_type`

These validate core structural correctness.

---

### 3. Scope assertions

- `assert_at_scope`
- `assert_check_at_scope`
- `assert_pairwise_scope`
- `assert_quantifier_scope`

They enforce correct AST typing for scopes.

---

### 4. Constraint assertions

- `assert_neighborhood`
- `assert_domain`
- `assert_backend`
- `assert_no_backend`

These validate optional property components.

---

### 5. Logic assertions

- `assert_pair`

Used to validate pairwise expressions.

---

## Design philosophy

Helpers are designed to:

- encode AST knowledge explicitly
- avoid repetitive low-level checks
- centralize validation logic
- improve readability of tests

They act as a lightweight "test DSL".