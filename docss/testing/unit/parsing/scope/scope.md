# Scope Model

## Definition

A scope defines the context in which a FORML assertion is evaluated.

Every property must define exactly one scope.

---

## Supported scopes

| Scope | Purpose |
|---|---|
| AT | Local robustness |
| CHECK_AT | Point validation |
| PAIRWISE | Relational comparison |
| FORALL | Universal quantification |
| EXISTS | Existential quantification |

---

## Shared structure

Scopes may optionally contain:

- neighborhoods
- domains
- backend constraints

---

## AST responsibility

Scopes are transformed into dedicated AST nodes.

Examples:

- `AtExprNode`
- `CheckAtExprNode`
- `PairwiseExprNode`
- `QuantifierExprNode`

---

## Core invariants

| Invariant | Description |
|---|---|
| Single scope | A property cannot define multiple scopes |
| Scope required | A property must define one scope |
| Stable AST typing | Scope must map to correct AST node |
| Explicit rejection | Invalid scopes must fail parsing |

---

## Tested by

| Test File |
|---|
| `test_at.py` |
| `test_check_at.py` |
| `test_pairwise.py` |
| `test_forall.py` |
| `test_exists.py` |