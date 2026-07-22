# IR1 Layer

> Status: P21.4 / Implemented / Stabilizing  
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
| `PointBindingIR` | Stable identity and binding kind of one input point. |
| `QuantifierBinderIR` | One ordered expanded quantifier frame. |
| `ModelEvaluationIR` | Structured `(model, point, output port)` evaluation identity. |
| `OutputObservableExpressionIR` | Declarative label or class-probability view of one shared evaluation. |
| `ClassLabelIR` | Canonical user-facing label selector retained as IR metadata. |
| `RestrictionIR` | Canonical `where` or neighborhood relation with provenance. |
| `NeighborhoodIR` | Perturbation space or local neighborhood. |
| `DomainIR` | Typed domain constraints with resolved subjects and preserved boundary/literal kinds. |
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
- preserving exact point identity across scope, domain, features and outputs;
- preserving ordered and alternating binder chains;
- preserving canonical restrictions separately from the property formula;
- representing indexed model outputs as structured model evaluations;
- representing public output observables separately from evaluation identity;
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
- exact point bindings and binding kinds;
- quantifier order and lexical depth;
- restriction and sugar provenance;
- model-evaluation identity;
- neighborhood parameters;
- domain restrictions;
- resolved entity references;
- logical structure;
- scalar-expression operands;
- arithmetic tree structure and inferred type metadata;
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

## Point and Quantifier Preservation

For a validated scope such as:

```forml
forall applicant => target <= 7
```

IR1 preserves:

```text
kind = quantifier
variables = {"applicant": "symbolic"}
points = (PointBindingIR("applicant", UNIVERSAL),)
binders = (QuantifierBinderIR(FORALL, applicant),)
```

The translator must not synthesize `_x` or rename the declared variable. Grouped
and nested binders are expanded in source order. Alternating chains remain
ordered and are not projected to one coarse quantifier.

The historical `variables` and homogeneous `quantifier` fields remain temporary
compatibility views for IR2 consumers that have not yet migrated.

---

## Typed Domain Preservation

`ScopeIR.domain` must preserve a typed domain representation.

Target conceptual shape:

```text
DomainIR(
    constraints=(
        IntervalConstraintIR(
            entity="x0",
            feature="a",
            lower=0.0,
            upper=3.0,
            lower_boundary=CLOSED,
            upper_boundary=OPEN,
        ),
        FiniteSetConstraintIR(
            entity="x0",
            feature="region",
            values=(EU, US),
        ),
    )
)
```

IR1 must not collapse domains into an untyped `name`/`args` dictionary. It preserves semantic resolution and source provenance while remaining backend-independent.

Each domain entry also carries the exact `PointBindingIR` owning the feature.

The later IR2/aggregation boundary lowers interval and finite-set constraints into logical assumptions tagged with `AssumptionSource.DOMAIN`.

---

## Scalar Expression Preservation

IR1 must preserve backend-independent scalar expression structure.

Target family:

```text
ScalarIR
├── ConstantIR
├── FeatureRefIR
├── ModelOutputRefIR
├── OutputObservableExpressionIR
├── UnaryArithmeticIR
└── BinaryArithmeticIR
```

Comparison becomes:

```text
ComparisonIR(
    left: ScalarIR,
    op: EnumComparisonOperator,
    right: ScalarIR,
)
```

Required guarantees:

- feature references reuse the exact resolved `PointBindingIR`;
- model-output references contain `ModelEvaluationIR(model, point, output_name)`;
- label and probability expressions retain observable kind and canonical label;
- repeated observables of the same model, point, and output reuse one evaluation identity;
- different points produce distinct evaluation identities;
- arithmetic operators are canonical;
- expression order and associativity are preserved;
- no Z3 expression is created;
- no unsupported nonlinear form is silently converted into an affine form;
- no latent decision value, logit, sklearn method, or backend term is introduced.

Logical normalization treats a complete `ComparisonIR` as an atom. Arithmetic children are not boolean-normalized.

## Restriction Preservation

`where` and lowered `neighborhood` relations remain available as a separate
`ScopeIR.restriction` artifact with origin and source span. The task query
contains the canonical language formula selected by semantic validation.

NNF rewrites the formula and restriction logical trees without changing:

- point identity;
- binder order;
- model-evaluation identity;
- source provenance.

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

## Specification Constant Lowering

A semantically resolved specification constant lowers to a typed constant scalar expression with provenance.

Conceptually:

```text
ConstantExpressionIR(
    value=0.20,
    dtype=FLOAT,
    source_kind=SPECIFICATION_CONSTANT,
    source_name="max_risk",
)
```

IR1 must not create an input feature or symbolic solver variable for the declaration.

The declaration name remains available for pretty printing, diagnostics and traceability even when the backend receives only the canonical literal value.

## Stabilization Requirements

| Topic | Required Action |
|---|---|
| Pairwise split | Use `~` as the pairwise separator, not comma. |
| Backend enum handling | Normalize backend names robustly. |
| Attribute translation | Use semantic annotations for resolved entities. |
| Pretty printer | Display actual comparison operators, not always equality. |
| Domain pretty output | Show explicit subjects, interval boundary kinds, finite-set members, and provenance. |
| Quantifier variables | Preserve the exact identifier declared by `forall <identifier>` or `exists <identifier>`. |
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
