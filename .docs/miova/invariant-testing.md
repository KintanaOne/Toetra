# Invariant Testing

> Status: planned / critical  
> Scope: invariant-driven validation of FORML artifacts and transitions  
> Audience: maintainers, verification engineers, mutation authors

## Purpose

Invariant testing checks whether FORML artifacts and transformations satisfy properties that must remain true.

Miova uses invariants to verify both:

- artifact state;
- transitions between artifacts.

## Invariant Categories

FORML should use two main invariant categories.

### State Invariant

A state invariant evaluates a single artifact.

Example:

```text
Every ComparisonIR must have an entity, feature, operator, and value.
```

### Transition Invariant

A transition invariant evaluates a before/after artifact pair.

Example:

```text
Semantic → IR1 must preserve resolved entity binding.
```

## Invariant Scope

| Layer | Example State Invariant |
|---|---|
| Source | Source must be non-empty and parse-targeted. |
| CST | Root node must be `program`. |
| AST | Program must contain a header and at least one property. |
| SemanticValidatedAST | Attributes must be resolved or explicitly rejected. |
| IR1 | Logical tree must contain no AST node. |
| IR1-NNF | Negation must only appear above atomic leaves. |
| IR2 | Output must satisfy selected CNF or DNF form. |
| ModelSchema | Feature names must be unique and typed. |
| AggregatedAssertionSet | Assertion groups must preserve origin traceability. |
| LoweredQuery | Simplification must not drop required constraints silently. |
| BackendQuery | Backend artifact must declare backend and capability assumptions. |

## Transition Invariants

| Transition | Example Transition Invariant |
|---|---|
| Source → CST | Parsing must be deterministic for identical source. |
| CST → AST | Required AST fields must not be `None`. |
| AST → Semantic | Valid attribute references must become resolved. |
| Semantic → IR1 | Resolved entity and feature must be preserved. |
| IR1 → IR2 | Logical meaning must be equivalent or equisatisfiable. |
| Model → Schema | Model feature metadata must be normalized. |
| Schema → Semantic | DSL attributes must reference known schema features. |
| Aggregation → Lowering | Removed constraints must be justified as redundant. |
| Lowering → Backend | Backend query must satisfy backend capability contract. |

## IR1-NNF Invariants

IR1 is the first normalized logical layer.

For the NNF-oriented IR1 stage, important invariants include:

- implication nodes are eliminated or marked for elimination;
- De Morgan transformations preserve meaning;
- negations are pushed toward atomic leaves;
- no backend-specific expression appears in IR1;
- semantic entity resolution is preserved.

## IR2 Normal-Form Invariants

IR2 is planned as the normal-form preparation layer.

For CNF:

- top-level structure is a conjunction of clauses;
- each clause is a disjunction of literals;
- literals are atomic predicates or negated atomic predicates.

For DNF:

- top-level structure is a disjunction of cases;
- each case is a conjunction of literals;
- literals preserve semantic origin.

## ModelSchema Invariants

A valid `ModelSchema` should satisfy:

- framework is known;
- model type is available;
- target is defined;
- task is defined;
- features are typed;
- feature names are unique;
- nullable metadata is explicit;
- framework-specific metadata is optional but namespaced.

## Aggregation Invariants

The AggregatedAssertionSet is a critical future artifact.

It should satisfy:

- every assertion has an origin;
- every model constraint has an origin;
- semantic constraints are not mixed silently with user assertions;
- contradictions are either represented or rejected;
- weakening/strengthening is explicitly tracked;
- backend assumptions are separated from user intent.

## Invariant Failure Semantics

Invariant failure is not always a bug.

It can mean:

- the mutation intentionally produced an invalid artifact;
- the contract correctly rejected the transition;
- the invariant is too strict;
- the implementation has a bug;
- the artifact kind was mislabeled.

Miova reports must distinguish these cases.

## P0 Requirement

At P0, FORML should define invariants for:

1. AST structural validity;
2. semantic binding resolution;
3. IR1 logical validity;
4. IR1-NNF shape;
5. ModelSchema consistency;
6. IR2 normal forms;
7. aggregation traceability;
8. backend query capability compliance.
