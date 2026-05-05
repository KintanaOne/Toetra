# `architecture/ast/scope_model.md`

# Scope Model

## 1. Purpose

Define semantic context structures used by AST properties.

---

## 2. Responsibilities

Scopes define:

- variable context,
- symbolic environments,
- perturbation semantics,
- domain constraints,
- neighborhood definitions.

---

## 3. Scope Types

| Type | Meaning |
|---|---|
| local | anchor + perturbation |
| pairwise | relationship between variables |
| quantifier | symbolic variable space |
| pointwise | single evaluation point |

---

## 4. Scope Semantics

Scopes introduce variable roles:

- anchor variables,
- perturbation variables,
- symbolic variables.

---

## 5. Invariants

- Scopes remain isolated.
- Variable role assignment remains deterministic.
- Scope hierarchy remains structurally valid.