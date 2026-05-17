# Semantic Parsing Tests

## Scope

These tests validate the semantic correctness of parsed AST programs.

---

## Focus areas

- AST node typing
- scope correctness
- domain consistency
- neighborhood consistency
- backend attachment correctness

---

## Validations performed

- correct AST class instantiation
- correct property structure
- correct domain binding
- correct neighborhood parsing

---

## Multiple properties

Ensures:

- program can contain multiple properties
- each property is independently valid
- different scope types coexist correctly

---

## Invalid cases

- multiple expressions in a body (if forbidden)
- missing expressions
- malformed program structure