# Lowering and Minimization Contract

> Status: P0 / Planned / Critical  
> Scope: AggregatedAssertionSet to LoweredQuery  
> Implementation: Not yet implemented  
> Audience: backend authors, optimization authors, solver integration authors

## Purpose

The Lowering and Minimization contract defines how a complete verification problem is simplified and shaped before backend encoding.

It answers the question:

```text
How can FORML reduce the verification problem while preserving correctness?
```

This layer is where logical simplification, redundancy elimination and backend-preparation occur.

---

## Input

```text
AggregatedAssertionSet
```

The input contains:

- user assertions;
- semantic constraints;
- model constraints;
- scope/domain/neighborhood constraints;
- origin metadata;
- preservation metadata.

---

## Output

```text
LoweredQuery
```

The output is still not a backend-specific query.

It is backend-preparable.

---

## Transformation Families

| Transformation | Purpose |
|---|---|
| Constant folding | Remove trivial boolean expressions. |
| Duplicate elimination | Remove repeated constraints. |
| Subsumption | Remove weaker constraints implied by stronger ones. |
| Dead branch pruning | Remove impossible DNF cases. |
| Clause simplification | Simplify CNF clauses. |
| Domain pruning | Remove impossible domain alternatives. |
| Backend-preparation rewrite | Shape expressions for supported backend capabilities. |

---

## Preservation Policy

Each transformation must record its preservation mode:

| Mode | Meaning |
|---|---|
| Equivalent | Same truth conditions. |
| Equisatisfiable | Same satisfiability result. |
| Conservative | May over-approximate or under-approximate and must be explicit. |

Unsafe minimization is not allowed silently.

---

## Guarantees

If lowering/minimization succeeds:

- the query is simpler or better shaped for backend compilation;
- removed constraints are traceable;
- preservation metadata exists;
- backend-independent semantics are still available;
- the backend boundary may safely consume the result.

---

## Non-Goals

This layer must not:

- produce final Z3/ERAN objects directly;
- execute the backend;
- drop constraints without trace;
- change semantics without declaring it;
- hide unsupported backend requirements.

---

## Failure Modes

Expected failures include:

- unsupported minimization pattern;
- conflicting constraints;
- transformation losing semantics;
- invalid aggregation input;
- impossible backend-preparation rewrite;
- unsupported preservation mode.

---

## Miova Hooks

Miova may mutate:

- aggregated assertion sets;
- simplification metadata;
- preservation mode;
- origin traces;
- lowered query structures;
- redundant or contradictory constraints.

Expected outcome:

```text
Invalid minimization → lowering rejection
Valid minimization   → BackendQuery generation may continue
```
