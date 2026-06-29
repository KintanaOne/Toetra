# Assertion Aggregation Contract

> Status: P0 / Planned / Critical  
> Scope: IR2 + semantic constraints + model constraints to AggregatedAssertionSet  
> Implementation: Not yet implemented  
> Audience: IR authors, backend authors, verification designers

## Purpose

The Assertion Aggregation contract defines how FORML builds the complete verification problem.

It answers the question:

```text
What exactly must be verified?
```

The backend should not receive isolated DSL assertions only. It should receive the complete logical problem.

---

## Input

```text
IR2 Normal Forms
+
SemanticConstraintSet
+
ModelConstraintSet
+
BackendCapabilityConstraints
```

Potential sources:

| Source | Examples |
|---|---|
| DSL assertion | `x'.age <= 30` |
| Scope semantics | `x'` is perturbation of `x` |
| Neighborhood | `distance(x, x') <= eps` |
| Domain | `category in {A, B}` |
| Quantifier | `forall _x` or `exists _x` |
| ModelBridge | feature dtype, target, task |
| Backend | supported functions/operators |

---

## Output

```text
AggregatedAssertionSet
```

The artifact should contain:

- a collection of logical assertions;
- origin metadata for each assertion;
- grouping information;
- preservation metadata;
- dependency information;
- diagnostic context;
- optional backend-preparation hints.

---

## Aggregation Principle

Aggregation must preserve meaning.

It should not randomly flatten all constraints if structure matters.

For example:

```text
property intent
+
scope constraints
+
model constraints
```

must be composed in a way that still reflects the original property semantics.

---

## Guarantees

If aggregation succeeds:

- all required constraint families are represented;
- every generated assertion is traceable to an origin;
- no backend-specific query has been emitted;
- the full verification problem is explicit;
- lowering and minimization may operate on the complete set.

---

## Non-Goals

Aggregation must not:

- perform final backend encoding;
- execute a solver;
- erase assertion origins;
- silently drop constraints;
- perform unsafe minimization without trace.

---

## Failure Modes

Aggregation should reject:

- missing required model constraints;
- incompatible constraint families;
- invalid IR2 structure;
- unresolved semantic references;
- backend constraints that make the request impossible;
- ambiguous quantifier or scope composition.

---

## Miova Hooks

Miova may mutate aggregation inputs by:

- removing a constraint family;
- duplicating constraints;
- corrupting origins;
- replacing CNF/DNF groups;
- introducing incompatible model constraints;
- deleting scope constraints.

Expected outcomes:

```text
Invalid aggregation → aggregation rejection
Valid but different aggregation → lowering may continue with trace
```
