# SemanticValidatedAST to IR1 Contract

> Status: P21.4 / Implemented and stabilizing  
> Scope: Semantic meaning to backend-independent verification task  
> Audience: IR maintainers, semantic maintainers and pretty-printer authors

## Purpose

IR1 detaches validated meaning from DSL syntax while preserving scope, scalar structure, domain structure and traceability.

---

## Input Preconditions

IR1 lowering accepts only a successfully validated property.

Required preconditions:

- quantified identifiers are registered and resolved;
- all input and target references have semantic resolution;
- scalar types are known or explicitly represented as unresolved model-dependent types allowed by contract;
- domain subjects and bounds are semantically valid;
- property/scope compatibility has passed.

---

## Output

Conceptually:

```text
VerificationTaskIR1(
    property_type,
    scope,
    query,
    backend_hint,
    requirements_seed,
    provenance,
)
```

Exact class names may evolve.

---

## ScopeIR Requirements

`ScopeIR` preserves the complete point environment required by the property:

```text
points = ordered PointBindingIR identities
binders = ordered QuantifierBinderIR frames
default_point = exact PointBindingIR | None
domain = typed DomainIR1 | None
restriction = RestrictionIR | None
provenance = source scope and sugar metadata
```

Every binder retains its quantifier kind, point identity, lexical depth, source
span, and generated/source status. Grouped binders are expanded left to right.
Alternating binders must not be flattened into one coarse quantifier.

The historical `variables` and `quantifier` fields remain compatibility
projections during migration. New consumers must not use them to reconstruct
point identity or alternation.

---

## Scalar IR Requirements

IR1 mirrors the validated scalar tree with backend-independent nodes:

```text
ConstantIR1
FeatureRefIR1
TargetRefIR1
OutputObservableExpressionIR1
UnaryArithmeticIR1
BinaryArithmeticIR1
ComparisonIR1(left_expression, operator, right_expression)
```

Each feature reference uses its resolved `PointBindingIR`, not raw unresolved
syntax or only a string entity label.

Each node retains enough metadata for:

- dtype/sort requirements;
- source mapping;
- diagnostics;
- recursive backend translation later.

IR1 does not flatten the expression into coefficients unless a separate explicit affine-canonicalization pass is invoked.

---

## Typed Domain IR1

`ScopeIR.domain` remains typed and backend-independent.

It preserves:

- entry subject as resolved feature reference;
- interval lower/upper scalar expressions;
- open/closed boundary kinds;
- finite-set member values and literal kinds;
- entry provenance;
- simultaneous/conjunctive domain semantics.

IR1 does not encode these constraints as Z3 expressions.

---

## Model Output Mapping

The DSL keyword `target` lowers to one structured model evaluation:

```text
TargetRefIR1(
    evaluation=ModelEvaluationIR(
        model_identity=<header model>,
        point=<resolved PointBindingIR>,
        target_name=<header target>,
    )
)
```

`target[x0]` and `target[x1]` therefore remain distinct even though V1 exposes
one selected output port. Repeated references to `target[x0]` reuse one interned
evaluation identity.

Classification observables lower without model-family rewriting:

```text
OutputObservableExpressionIR(
    evaluation=ModelEvaluationIR(model, point, output_name),
    observable=PREDICTED_LABEL | CLASS_PROBABILITY,
    label=ClassLabelIR(...) | None,
    dtype=<validated scalar type>,
)
```

Observable kind and label are not part of evaluation identity. Two probability
expressions for different labels remain distinct expressions but reuse one model
evaluation. The historical `_model.<target>` fields remain compatibility
projections for scalar regression; they are not the source of truth.

## Restriction Mapping

Canonical `where` and neighborhood restrictions are preserved separately in
`ScopeIR.restriction`, including source origin and source span. The property
query contains the canonical language formula produced by semantic validation.

NNF normalization may rewrite the logical shape of both formula and
restriction, but it must preserve point identities, evaluation identities,
binder ordering, and provenance.

---

## Query Preservation

Boolean structure remains backend-independent.

A scalar comparison is a logical atom. IR1 may subsequently enter NNF normalization, but arithmetic subtrees are not logical subtrees.

---

## Requirements Seed

IR1 lowering may emit or preserve requirement metadata discovered semantically:

- scalar sorts;
- affine/nonlinear arithmetic flags;
- finite-set/categorical requirements;
- target/model assumptions;
- domain presence;
- quantifier verification semantics.

The definitive backend-compatibility decision remains later.

---

## Postconditions

A valid IR1 task contains:

- no Lark node;
- no unresolved attribute;
- no semantic alias guess;
- no opaque `Domain(name, raw_args)` representation;
- no asymmetric feature-to-constant-only comparison restriction;
- no solver-native object;
- preserved point identity, binder order, binding kind and source provenance;
- structured model evaluation identity for every target reference.

---

## Failure Ownership

IR1 lowering rejects an allegedly validated input when:

- required semantic annotations are missing;
- a resolved entity/path cannot be produced;
- a scalar node lacks inferred type required by the IR contract;
- a typed domain is incomplete;
- quantifier kind or bound variable was lost;
- target resolution is inconsistent with the program header.

These are compiler-contract failures, not user backend-capability errors.

## Specification Constant Lowering Addendum

A resolved specification constant becomes a typed constant-valued scalar IR node.

The lowering preserves:

- canonical value;
- canonical dtype;
- declaration name;
- source kind `SPECIFICATION_CONSTANT`;
- source provenance when available.

It must not become:

- `AttributeIR`;
- model output IR;
- an unconstrained solver variable;
- an unresolved symbolic name.

## Patch 21 Output-Observable Addendum

ADR-0023 amends the scalar-only `TargetRefIR1` mapping for the Patch 21 target.
IR1 must represent separately:

```text
ModelEvaluationIR(model, point, output_port)
OutputObservableIR(evaluation, observable_kind, optional_label)
```

P21.4 implements this split with `ModelEvaluationIR`,
`OutputObservableExpressionIR`, and `ClassLabelIR`. The invariants remain
normative:

- several observables at the same point reuse one evaluation identity;
- different labels remain distinct observable expressions;
- source observable kind and label survive into IR1;
- internal model quantities are not introduced by ordinary semantic-to-IR1
  lowering;
- existing scalar regression references remain a compatibility projection of the
  regression-value observable.

See [Model Semantic Lowering](model-semantic-lowering.md) for the later boundary
that may introduce model-family-specific canonical constraints.
