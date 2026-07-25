# Assertion Aggregation

> Status: P0 / Planned / Critical  
> Scope: Combining DSL assertions, semantic constraints, and model constraints  
> Implementation: Not yet implemented  
> Audience: backend authors, IR authors, ModelBridge authors, verification designers

## Purpose

Assertion aggregation is the planned layer that combines all constraints required to form a complete verification problem.

It answers the question:

```text
What is the full logical problem that the backend must verify?
```

The backend should not receive isolated DSL assertions only. It should receive an aggregated verification problem.

---

## Position in the Pipeline

```text
IR2 / CNF-DNF
    +
Semantic constraints
    +
ModelBridge-derived constraints
    ↓
Assertion Aggregation
    ↓
AggregatedAssertionSet
```

---

## Why Aggregation Exists

A Toetra property is not only its RHS assertion.

A complete verification query may involve:

- user assertions;
- scope constraints;
- neighborhood constraints;
- domain constraints;
- quantifier constraints;
- model feature constraints;
- model task constraints;
- target constraints;
- backend capability constraints.

Aggregation is the layer where these constraints become a single verification problem.

---

## Inputs

Assertion aggregation may consume:

| Input | Origin | Example |
|---|---|---|
| User assertions | Toetra Specification Language / IR2 | `x'.age <= 30` |
| Scope constraints | Semantic layer | `x'` is perturbation of `x` |
| Neighborhood constraints | LHS / semantic context | `distance(x, x') <= eps` |
| Domain constraints | LHS / domain | `x.category in {A, B}` |
| Model schema constraints | ModelBridge | feature exists and has dtype |
| Model behavior constraints | future model encoding | model output relation |
| Backend capability constraints | backend registry | unsupported predicate rejection |

---

## Output

The output should be an explicit artifact:

```text
AggregatedAssertionSet
```

A future `AggregatedAssertionSet` may contain:

- property identifier;
- normalized logical assertions;
- semantic constraints;
- model constraints;
- scope constraints;
- preservation metadata;
- traceability links;
- backend hint;
- diagnostics context.

---

## Aggregation Semantics

Aggregation must define how constraints are composed.

Common composition rules:

| Constraint Type | Composition |
|---|---|
| Required assumptions | conjunction |
| Alternative cases | disjunction |
| Domain restrictions | conjunction |
| Model input constraints | conjunction |
| Backend unsupported constraints | diagnostic / early stop |
| Counterexample search branches | disjunction or case split |

---

## Example

A user property:

```toetra
[ROBUSTNESS]: forall baseline, candidate => CLASSIFICATION.EQUAL()
```

May produce an aggregated problem containing:

```text
User intent:
    CLASSIFICATION.EQUAL()

Scope constraints:
    x is anchor
    x' is perturbation

Neighborhood constraints:
    L2(x, x') <= 0.1

Model constraints:
    x and x' must match model input schema
    model task must be classification

Target constraint:
    target exists and is compatible
```

---

## Guarantees

Assertion aggregation must guarantee:

- all required constraints are explicit;
- no semantic constraint is silently dropped;
- model constraints are represented separately from user assertions;
- traceability is preserved;
- backend-incompatible constraints are diagnosed;
- aggregation does not execute verification;
- aggregation does not encode backend-specific solver objects.

---

## Non-Goals

Aggregation must not:

- parse source code;
- build AST nodes;
- perform model loading;
- select final backend implementation;
- call Z3 directly;
- hide minimization decisions.

---

## Relation to ModelBridge

ModelBridge provides normalized model information.

Aggregation uses ModelBridge outputs to include model-side constraints.

ModelBridge itself should not aggregate DSL assertions. It should provide the schema and model-derived facts needed by this layer.

---

## Relation to Lowering / Minimization

Aggregation creates the complete problem.

Lowering and minimization optimize or simplify that problem before backend-specific encoding.

Therefore:

```text
Aggregation = completeness
Lowering/minimization = preparation and simplification
```

---

## Relation to Miova

Miova can mutate aggregated assertion sets to test:

- missing constraint detection;
- duplicated constraint handling;
- invalid model constraint handling;
- traceability preservation;
- expected backend rejection;
- robustness of minimization inputs.
