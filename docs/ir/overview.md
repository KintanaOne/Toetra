# Intermediate Representations Overview

> Status: Stabilizing  
> Implementation: Implemented until IR1; IR2, aggregation, lowering, and backend query are planned  
> Scope: Logical verification pipeline

## Purpose

Intermediate Representations, or IRs, are the internal logical representations used by FORML after DSL parsing and semantic validation.

Their purpose is to progressively transform user intent from a domain-specific property expression into a backend-preparable verification problem.

FORML does not directly send DSL assertions to a solver or verification backend. Instead, it progressively formalizes them through several layers:

```text
SemanticValidatedAST
    ↓
IR1 — normalized logical representation
    ↓
IR2 — backend-preparation normal forms
    ↓
AggregatedAssertionSet
    ↓
LoweredQuery
    ↓
BackendQuery
```

This layered approach keeps DSL syntax, semantic validation, logical normalization, model constraints, and backend encoding separated.

---

## Why IRs Matter

The DSL captures what the user wants to verify.

The IR pipeline defines how FORML turns that intent into a formal verification problem.

IRs are necessary because FORML must support several concerns at once:

| Concern | Why it matters |
|---|---|
| DSL independence | Backends should not depend on source syntax. |
| Semantic preservation | Logical meaning must survive transformations. |
| Normalization | Logical expressions need canonical forms. |
| Backend preparation | Different solvers may require different encodings. |
| Model integration | ModelBridge-derived constraints must be composed with DSL assertions. |
| Mutation testing | Miova must be able to challenge each representation boundary. |

---

## IR Pipeline

### SemanticValidatedAST

The semantic layer resolves variables, scopes, implicit entities, property compatibility, and logical correctness.

It produces an AST enriched with semantic annotations.

This is not yet an IR, but it is the required input for IR translation.

---

### IR1

IR1 is the first backend-independent logical representation.

It currently represents verification tasks composed of:

- property type,
- scope representation,
- logical query,
- optional backend hint.

IR1 is responsible for early logical normalization, including implication handling, De Morgan transformations, and Negation Normal Form where applicable.

IR1 answers:

```text
What is the normalized logical task to verify?
```

---

### IR2

IR2 is the planned layer responsible for clause-oriented or case-oriented normal forms.

It may produce:

- CNF for conjunction-of-clauses reasoning,
- DNF for scenario splitting or counterexample exploration,
- other canonical forms required by backend strategy selection.

IR2 answers:

```text
Which logical form is best suited for the verification strategy?
```

---

### AggregatedAssertionSet

The aggregation layer combines multiple sources of constraints:

- user DSL assertions,
- semantic constraints,
- scope constraints,
- neighborhood constraints,
- domain constraints,
- model constraints derived from ModelBridge,
- backend capability constraints when needed.

It answers:

```text
What is the complete verification problem?
```

---

### LoweredQuery

The lowering and minimization layer simplifies and prepares the aggregated assertion set.

It may perform:

- redundancy elimination,
- logical simplification,
- constraint minimization,
- backend-aware preparation,
- trace-preserving transformations.

It answers:

```text
What is the smallest or most suitable backend-preparable query?
```

---

### BackendQuery

BackendQuery is the final backend-specific artifact sent to a verification engine.

Examples may include:

- a Z3 formula,
- an ERAN-compatible robustness query,
- a future backend-specific verification artifact.

It answers:

```text
What exactly is sent to the backend?
```

---

## Current Implementation Status

| Representation | Status | Notes |
|---|---|---|
| SemanticValidatedAST | implemented / stabilizing | Semantic annotations and binding exist. |
| VerificationTask | implemented / stabilizing | Main IR1 execution unit. |
| ScopeIR | implemented / stabilizing | Represents pointwise, local, pairwise, and quantifier contexts. |
| LogicalIR | implemented / stabilizing | Represents comparisons, boolean operators, implications, problem predicates, and target scalar-expression evolution. |
| Specification constant lowering | accepted target / implementation pending | Constants become typed IR literals with declaration provenance. |
| IR1-NNF | implemented / stabilizing | De Morgan / NNF logic exists conceptually and should be explicitly documented and tested. |
| IR2-CNF/DNF | planned | Required after IR1 for backend preparation. |
| AggregatedAssertionSet | planned | Required to combine DSL and model-derived constraints. |
| LoweredQuery | planned | Required before backend-specific encoding. |
| BackendQuery | planned | Required for Z3 and future backend integration. |

---

## Design Principle

FORML treats IRs as architectural contracts.

Each IR layer must define:

- its accepted inputs,
- its produced outputs,
- its invariants,
- its semantic preservation guarantees,
- its relationship to previous and next layers,
- its mutation boundaries.

This ensures that the logical verification pipeline can evolve without collapsing into a single unstructured compiler pass.

---

## Related Documents

- [Verification Task](verification-task.md)
- [Scope IR](scope-ir.md)
- [Logical IR](logical-ir.md)
- [IR1 NNF](ir1-nnf.md)
- [IR2 Normal Forms](ir2-normal-forms.md)
- [Aggregated Assertion Set](aggregated-assertion-set.md)
- [Backend Query](backend-query.md)
