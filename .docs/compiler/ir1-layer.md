# IR1 Layer

> Status: P0 / Implemented / Stabilizing  
> Scope: SemanticValidatedAST to IR1  
> Implementation: VerificationTask and logical IR tree  
> Audience: IR authors, backend authors, testing authors

## Purpose

IR1 is the first backend-independent logical representation of a validated FORML property.

It answers the question:

```text
What is the normalized logical verification task represented by this property?
```

IR1 is not yet a backend query. It is the first formal logical layer after semantic validation.

---

## Position in the Pipeline

```text
SemanticValidatedAST
    ↓
IR1
    ↓
IR2
```

IR1 receives semantically validated properties and produces backend-independent verification tasks.

---

## Main IR1 Artifacts

| Artifact | Meaning |
|---|---|
| `VerificationTask` | Top-level verification unit for one property. |
| `ScopeIR` | Semantic scope extracted from LHS. |
| `NeighborhoodIR` | Perturbation space or local neighborhood. |
| `DomainIR` | Optional domain restriction. |
| `QueryIR` | RHS verification expression. |
| `LogicalIR` | Boolean tree representation. |
| `ComparisonIR` | Atomic comparison predicate. |
| `ProblemIR` | High-level ML problem predicate. |

---

## VerificationTask

A `VerificationTask` represents one property prepared for logical processing.

It contains:

- property type;
- scope;
- query;
- optional backend hint.

Conceptually:

```text
VerificationTask(
    property_type=ROBUSTNESS,
    scope=ScopeIR(...),
    query=QueryIR(...),
    backend=Z3 | None,
)
```

---

## IR1 Responsibilities

IR1 is responsible for:

- representing semantic scope explicitly;
- representing RHS logic as backend-independent nodes;
- preserving resolved semantic bindings;
- flattening associative boolean operators where appropriate;
- preparing logic for normalization;
- supporting De Morgan and NNF transformations;
- serving as the input to IR2.

---

## IR1-NNF

IR1 owns early logical normalization, including:

- implication elimination when required;
- De Morgan transformations;
- pushing negations inward;
- producing or preserving Negation Normal Form;
- ensuring negation appears only over atomic predicates when NNF is finalized.

This means NNF should be documented as an IR1 invariant or IR1 subphase.

---

## What IR1 Must Preserve

IR1 must preserve:

- property type;
- semantic scope kind;
- variable roles;
- neighborhood parameters;
- domain restrictions;
- resolved entity references;
- logical structure;
- problem/function intent;
- backend hint, if present.

---

## What IR1 Must Not Do

IR1 must not:

- choose CNF or DNF;
- aggregate multiple properties;
- inject model-derived constraints;
- perform solver-specific encoding;
- produce Z3 expressions;
- perform backend-specific minimization.

Those responsibilities belong to IR2, aggregation, lowering, or backend-specific compilers.

---

## Semantic Resolution Requirement

IR1 translation must use semantic information.

Example:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => age <= 30
```

The raw AST may contain:

```text
AttributeNode(entity=None, feature="age")
```

After semantic validation, the resolved meaning is:

```text
x'.age
```

IR1 should encode:

```text
ComparisonIR(entity="x'", feature="age", op="<=", value=30)
```

not:

```text
ComparisonIR(entity=None, feature="age", ...)
```

---

## IR1 Output

The output of IR1 is a list of verification tasks:

```text
list[VerificationTask]
```

Each property becomes one task initially. Later aggregation may combine tasks or constraints into a larger verification problem.

---

## Guarantees

IR1 must guarantee:

- no AST-specific objects leak into backend layers;
- no raw parser structures remain;
- logical expressions are explicit;
- semantic scope is explicit;
- resolved attributes are used when available;
- NNF/De Morgan transformations preserve semantics;
- backend hints remain metadata, not backend execution.

---

## Stabilization Requirements

| Topic | Required Action |
|---|---|
| Pairwise split | Use `~` as the pairwise separator, not comma. |
| Backend enum handling | Normalize backend names robustly. |
| Attribute translation | Use semantic annotations for resolved entities. |
| Pretty printer | Display actual comparison operators, not always equality. |
| Domain pretty output | Correct domain args display. |
| Quantifier variables | Preserve symbolic variable convention such as `_x`. |
| NNF location | Make NNF an explicit IR1 transformation stage. |

---

## Relation to IR2

IR2 consumes IR1.

IR1 provides normalized logical structure. IR2 decides the shape needed for later verification:

- CNF for conjunction-of-clauses workflows;
- DNF for case-splitting workflows;
- other canonical forms if needed.

---

## Relation to Miova

Miova can mutate IR1 artifacts to test:

- logical normalization invariants;
- scope preservation;
- semantic binding preservation;
- unsupported node handling;
- invalid `VerificationTask` rejection;
- NNF invariants.
