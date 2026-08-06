# Language overview

> Status: Current for `1.0.0rc4`
> Scope: Public Toetra Specification Language surface
> Audience: users, compiler contributors, and reviewers

## Purpose

The Toetra Specification Language expresses behavioral properties over machine
learning models. Users describe model inputs, points, admissible domains, model
outputs, and assertions without writing framework calls, solver variables, or
backend-native formulas.

A `.toetra` file is the human-facing input to the verification pipeline. It is
not itself a model format or proof backend.

## Read support correctly

Toetra deliberately separates three questions:

1. Does the source parse?
2. Does it have accepted meaning for the bound points and model schema?
3. Does a released V1 route execute it?

Read [Language support levels](support-levels.md) before treating any grammar
construct as supported. The [Public V1 profile](../public-v1-profile.md) is the
source of truth for executable framework/model/backend combinations.

## Program shape

A program contains a header followed by one or more properties:

```toetra
model := "linear.joblib"
target := score

maximum_score := 7.0

[BOUND]:
forall applicant
with domain(
    applicant.income: [0.0, 100000.0]
)
=> target[applicant] <= maximum_score using Z3
```

The header declares:

- one model artifact;
- one target identity;
- an optional dataset;
- optional immutable specification constants;
- optional inline or referenced anchors.

Each property contains:

- a property label;
- an optional point scope;
- optional domains or restrictions owned by that scope;
- one Boolean assertion;
- an optional backend selection.

## Core language concepts

### Points and evaluations

Symbolic points are introduced by `forall` or `exists`. Concrete points are
declared as anchors. Brackets on `target` select the input point used for one
model evaluation:

```toetra
target[baseline]
target[candidate]
```

They do not select an output index. When exactly one eligible default point is
visible, the short form `target` denotes its evaluation.

### Domains

Domains constrain explicitly qualified input features:

```toetra
with domain(
    applicant.age: [18, 65],
    applicant.segment_id: {1, 2, 3}
)
```

The four interval bracket combinations preserve open and closed endpoints.
Finite sets preserve discrete membership. A domain is an assumption over model
inputs, never an assertion over the model output.

### Assertions

Assertions combine typed scalar comparisons:

```toetra
2 * applicant.income - applicant.debt >= 0
target[applicant] <= maximum_score
```

with Boolean operators:

```toetra
and
or
not
->
```

Uppercase `AND`, `OR`, and `NOT` are also accepted. Arithmetic trees are typed
and classified before route selection. The built-in V1 route supports the
numeric-affine subset; broader parsed arithmetic is never silently linearized.

### Model output observables

Regression uses the scalar model evaluation:

```toetra
target[applicant]
```

Binary classification exposes declarative user-facing observables:

```toetra
target[applicant].label
target[applicant].probability("approved")
```

Framework implementation details such as logits, class indices, or
`decision_function` are not DSL observables.

### Specification constants

Header constants name immutable scalar values:

```toetra
maximum_risk := 0.20
minimum_income := 25000.0
region := "EU"
```

They are resolved before lowering and never become mutable runtime variables.

### Backend declarations

An explicit declaration is a required backend selection:

```toetra
using Z3
```

If no backend is written, the router selects the first registered backend whose
capabilities satisfy the verification task. The built-in V1 registry contains
only Z3. Other names recognized by the grammar are reserved and do not imply
execution support.

## As-built compilation path

The current implementation follows this path:

```text
source
→ CST
→ AST
→ semantic validation
→ IR1
→ model-semantic lowering
→ NNF
→ IR2 plus assumptions and requirements
→ route qualification
→ backend translation and execution
→ report, provenance, and replay
```

The language layer owns source structure. Semantic validation owns bindings,
types, point identities, and model-output meaning. Backends receive qualified
IR2 tasks and do not repair invalid language semantics.

## Public V1 boundary

The public V1 routes are intentionally narrow:

- fitted single-output scikit-learn `LinearRegression`;
- direct fitted binary scikit-learn `LogisticRegression`;
- finite transformed numeric inputs;
- homogeneous universal or existential point bindings;
- numeric domains and affine arithmetic;
- the built-in Z3 backend;
- structured reports, provenance, and concrete replay.

The exact inclusions and exclusions live in the
[Public V1 profile](../public-v1-profile.md). Internal code, vocabulary, or
parser recognition cannot widen that profile.

## Reference map

| Need | Page |
|---|---|
| Interpret support claims | [Language support levels](support-levels.md) |
| See the complete user syntax | [Syntax](syntax.md) |
| Inspect grammar ownership and precedence | [Grammar](grammar.md) |
| Review recognized words and reserved names | [Vocabulary](vocabulary.md) |
| Bind points and concrete anchors | [Scopes](scopes.md) |
| Understand multi-point evaluation identity | [Points, anchors, and evaluations](points-anchors-and-evaluations.md) |
| Constrain inputs | [Domains](domains.md) |
| Write predicates | [Assertions](assertions.md) |
| Write scalar arithmetic | [Arithmetic expressions](arithmetic-expressions.md) |
| Select regression or classification output views | [Model output observables](model-output-observables.md) |
| Reuse thresholds and literals | [Specification constants](specification-constants.md) |
| Understand property labels | [Properties](properties.md) |
| Select a backend | [Backends syntax](backends.md) |
| Compare accepted and rejected forms | [Examples](examples.md) and [Invalid examples](invalid-examples.md) |

For internal compiler ownership, use the
[as-built architecture](../architecture/overview.md) and accepted contracts.
