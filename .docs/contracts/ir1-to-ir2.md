# IR1 to IR2 Contract

> Status: P0 / Planned / Critical  
> Scope: IR1-NNF to IR2 normal forms  
> Implementation: Not yet implemented  
> Audience: IR authors, solver integration authors, backend authors

## Purpose

The IR1 to IR2 contract defines how normalized logical tasks are transformed into forms better suited for aggregation, minimization and backend preparation.

It answers the question:

```text
Which normal form should this verification problem use next?
```

IR2 is the layer for CNF, DNF and future backend-preparation logical forms.

---

## Input

```text
IR1 / VerificationTask
```

Preconditions:

- semantic bindings have already been resolved;
- logical expression is backend-independent;
- NNF invariant is satisfied when required;
- no backend-specific query has been produced.

---

## Output

```text
IR2 / NormalFormIR
```

The output may represent:

- CNF;
- DNF;
- another explicit normal form;
- a selected representation with metadata explaining why it was chosen.

---

## Normal Form Selection

IR2 may select a form based on:

| Need | Preferred Form |
|---|---|
| SAT/SMT-style global consistency | CNF |
| Clause-level simplification | CNF |
| Case splitting | DNF |
| Scenario exploration | DNF |
| Counterexample search | DNF or backend-specific preparation |
| Backend requirement | backend-compatible normal form |

---

## Equivalence Policy

IR2 transformations must declare their preservation mode.

| Mode | Meaning |
|---|---|
| Semantic equivalence | The transformed formula has the same truth value for every assignment. |
| Equisatisfiability | The transformed formula has the same satisfiability result, possibly with auxiliary variables. |
| Approximation | The transformation is intentionally conservative or relaxed and must be explicitly marked. |

The default expectation is semantic equivalence unless the transformation explicitly declares otherwise.

---

## Guarantees

If IR2 translation succeeds:

- the output form is explicit;
- the transformation preservation mode is known;
- traceability to IR1 is preserved;
- no backend-specific object is emitted yet;
- aggregation can consume the IR2 artifact without re-normalizing from AST.

---

## Non-Goals

IR2 must not:

- introduce model constraints;
- aggregate multiple property assertions;
- perform backend-specific encoding;
- execute solver calls;
- erase traceability.

---

## Failure Modes

IR2 should reject:

- malformed IR1 trees;
- unsupported logical operators;
- non-normalizable expressions;
- transformations that would lose semantics without explicit declaration;
- backend-requested forms not supported by the current IR2 implementation.

---

## Miova Hooks

Miova may mutate IR1 or IR2 by:

- inserting malformed negations;
- breaking clause structure;
- replacing CNF with DNF metadata;
- deleting trace metadata;
- introducing unsupported logical nodes;
- corrupting preservation mode.

Expected outcome:

```text
Invalid normal-form mutation → IR2 rejection or invariant failure
Valid normal-form mutation   → aggregation may continue
```
