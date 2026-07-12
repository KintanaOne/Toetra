# SemanticValidatedAST to IR1 Contract

> Status: P0 / Accepted target lowering  
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

For a quantified property, `ScopeIR` preserves:

```text
kind = QUANTIFIED
quantifier = FORALL | EXISTS
variables = {source_identifier: SYMBOLIC}
default_entity = source_identifier
domain = typed DomainIR1 | None
```

The quantifier kind must not be discarded under a generic `kind="quantifier"` field without another field preserving `FORALL` versus `EXISTS`.

---

## Scalar IR Requirements

IR1 mirrors the validated scalar tree with backend-independent nodes:

```text
ConstantIR1
FeatureRefIR1
TargetRefIR1
UnaryArithmeticIR1
BinaryArithmeticIR1
ComparisonIR1(left_expression, operator, right_expression)
```

Each reference uses resolved identity, not raw unresolved syntax.

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

## Target Mapping

The DSL keyword `target` lowers to a model-output reference tied to the header-declared target identity, for example conceptually:

```text
TargetRefIR1(entity="_model", feature=<declared target>)
```

The concrete internal entity label may differ, but it must remain distinct from input entities and consistent with model assumptions.

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
- preserved quantifier kind and variable identity.

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
