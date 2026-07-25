# Language Overview

> Status: Stabilizing  
> Scope: Public DSL surface  
> Priority: P1  
> Audience: Toetra users, compiler contributors, test authors

## Purpose

The Toetra language is a domain-specific language for expressing behavioral properties over machine learning systems.

Its role is to let a user describe what a model should satisfy, without directly writing solver constraints, backend-specific queries, or framework-specific model encodings.

A Toetra specification connects three concerns:

1. **The model under verification** — declared in the header.
2. **The target or output of interest** — declared in the header.
3. **Reusable specification constants** — optional immutable values naming business thresholds.
4. **The properties to verify** — expressed as scoped assertions.

The language is intentionally designed to be compiled through a sequence of progressively more formal representations:

```text
.toetra source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1 / NNF
→ IR2 / CNF-DNF
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
```

The DSL is therefore not the verification backend. It is the human-facing entry point of the Toetra verification pipeline.

---

## Design Goals

The Toetra language aims to provide:

| Goal | Meaning |
|---|---|
| Readability | Properties should be understandable by ML engineers and verification engineers. |
| Formal structure | Every expression must compile into structured AST and IR artifacts. |
| Explicit scope | Each property must define where it is evaluated. |
| Backend independence | The DSL should not encode backend-specific constraints directly. |
| Semantic binding | Specification constants, implicit features and explicit variables must be resolved before IR lowering. |
| Mutation testability | Language artifacts must be suitable for Miova and Hypothesis campaigns. |

---

## Current Language Shape

A Toetra program currently contains:

```text
header
body
```

The header declares at least:

```toetra
model := "model.joblib"
target := prediction
```

The header may also declare reusable immutable specification constants:

```toetra
max_risk := 0.20
minimum_income := 25000.0
```

The body contains one or more property sections:

```toetra
[ROBUSTNESS]: forall baseline, candidate => CLASSIFICATION.EQUAL()
```

A property has:

| Element | Role |
|---|---|
| Property type | Describes the verification intent, such as `ROBUSTNESS`, `BOUND`, `FAIRNESS`. |
| Scope | Defines where the property is evaluated, such as `at`, `check_at`, `pairwise`, or `forall`. |
| Domain | Optionally restricts admissible input valuations with typed intervals or finite sets. |
| Assertion | Defines what must hold in that scope. |
| Optional backend | Suggests or selects a verification backend. |

---

## Specification Constants

Specification constants name immutable scalar values used by domains and assertions:

```toetra
max_risk := 0.20
max_ratio := 0.35

[LOGIC]:
forall applicant
    => target <= max_risk
       AND applicant.debt <= max_ratio * applicant.income
```

Bare identifiers remain user-friendly. In assertions, a name resolves first to a matching specification constant and otherwise to an implicit feature of the scope's default entity. Explicitly qualified references such as `applicant.max_risk` always denote features. Domain subjects and feature references inside domain bounds remain explicit, while constants may be used by bare name.

See [Specification Constants](specification-constants.md).

## Typed Domains

A typed domain restricts the admissible values of explicitly qualified input features:

```toetra
[LOGIC]:
forall x0
    with domain(
        x0.a: [0.0, 3.0],
        x0.b: {obj1, obj2},
        x0.c: ]0.0, 3.0[
    )
    => target <= 7
```

Domain entries are assumptions over model inputs. They are not model-output assertions.

The language distinguishes:

- closed and open numeric interval bounds;
- finite discrete sets;
- quoted strings and symbolic categorical literals;
- domain subjects from assertion expressions.

Domain subjects are always explicit (`x0.a`) so semantic validation can verify that their entity is declared by the enclosing scope. The complete normative contract is defined in [Domains](domains.md).

---

## Arithmetic Expressions

Toetra comparisons accept expressions on both sides:

```toetra
2 * x0.a + x0.b <= target
```

Arithmetic expressions may also define interval bounds:

```toetra
with domain(
    x0.a: [x0.b - 1.0, x0.b + 1.0]
)
```

The public language supports a structured arithmetic tree. The first end-to-end verification profile is affine: addition, subtraction, unary signs, multiplication by a constant, and division by a non-zero constant.

Logical normal forms treat each comparison as an atom and do not rewrite inside arithmetic subexpressions. See [Arithmetic Expressions](arithmetic-expressions.md).

## Language vs Semantics

The Toetra language defines syntax. The semantic layer defines meaning.

For example:

```toetra
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => age <= 30
```

The raw DSL contains an implicit feature access:

```text
age
```

The semantic layer resolves it using the scope:

```text
x'.age
```

This distinction is critical:

- The language does not need users to write every internal variable explicitly.
- The semantic layer must make all bindings explicit before IR translation.
- IR layers must consume resolved semantic information, not raw syntax guesses.

---

## Relationship with ModelBridge

The language can reference features and task-level predicates, but it does not know by itself whether these references exist in the actual model or dataset.

ModelBridge provides a normalized `ModelSchema` used to connect DSL references with model metadata.

The target architecture uses the language and ModelBridge together:

```text
.toetra source
+ ModelSchema
→ schema-aware semantic validation
→ model-aware constraints
→ backend-ready verification query
```

This means the language is only one side of the end-to-end verification problem. The other side is the model representation.

---

## Relationship with Miova and Hypothesis

The Toetra language should be testable through:

- grammar-level samples,
- parser tests,
- AST builder tests,
- semantic contract tests,
- property-based generation with Hypothesis,
- intelligent fuzzing,
- Miova artifact mutations.

Language documentation must therefore describe not only valid syntax, but also expected invalid forms and boundary cases.

---

## Current Status

| Area | Status | Notes |
|---|---|---|
| Header syntax | implemented | `model`, one scalar `target`, optional dataset/schema inputs and specification constants. |
| Property sections | implemented | Direct assertions, ordered binders, domains, restrictions and optional backend. |
| Point bindings and sugar | implemented | Inline/referenced anchors, `check_at`, new `at`, indexed targets and stable legacy diagnostics. |
| Typed domains | implemented | Explicit point subjects, open/closed intervals, finite sets and arithmetic bounds. |
| Specification constants | implemented | Immutable typed declarations with deterministic name resolution. |
| Assertions | implemented | Scalar arithmetic, comparisons, boolean logic and supported predicates. |
| Quantifiers | implemented / capability-gated | Homogeneous chains execute; alternation is represented and rejected by current Z3 capabilities. |
| Model-aware validation | implemented | `ModelSchema` controls point feature names and types. |
| Backend syntax | implemented | Z3 is the executable V1 backend; other names do not imply support. |

## Related Documents

- [Grammar](grammar.md)
- [Vocabulary](vocabulary.md)
- [Syntax](syntax.md)
- [Properties](properties.md)
- [Scopes](scopes.md)
- [Domains](domains.md)
- [Specification Constants](specification-constants.md)
- [Assertions](assertions.md)
- [Arithmetic Expressions](arithmetic-expressions.md)
- [Specification Constants](specification-constants.md)
- [Backends Syntax](backends.md)
- [Examples](examples.md)

---

## Documentation-First Language Baseline

The accepted language evolution is defined by:

- explicit quantified bindings: `forall <identifier>` and `exists <identifier>`;
- typed domains with bracket-only open/closed interval notation;
- finite sets with numeric or symbolic members;
- scalar expression comparisons;
- specification constants with user-friendly bare-name resolution;
- exact semantic binding and capability-driven backend rejection.

The normative behavioral references are:

- [Normative Examples](examples.md)
- [Invalid and Unsupported Examples](invalid-examples.md)
- [Quantified Bindings](quantified-bindings.md)
- [Domains](domains.md)
- [Specification Constants](specification-constants.md)
- [Arithmetic Expressions](arithmetic-expressions.md)
- [Specification Constants](specification-constants.md)
- [Language Evolution Test Matrix](../testing/language-evolution-test-matrix.md)

Implementation must follow these documents rather than infer intended behavior from the current code snapshot.
