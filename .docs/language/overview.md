# Language Overview

> Status: Stabilizing  
> Scope: Public DSL surface  
> Priority: P1  
> Audience: FORML users, compiler contributors, test authors

## Purpose

The FORML language is a domain-specific language for expressing behavioral properties over machine learning systems.

Its role is to let a user describe what a model should satisfy, without directly writing solver constraints, backend-specific queries, or framework-specific model encodings.

A FORML specification connects three concerns:

1. **The model under verification** — declared in the header.
2. **The target or output of interest** — declared in the header.
3. **The properties to verify** — expressed as scoped assertions.

The language is intentionally designed to be compiled through a sequence of progressively more formal representations:

```text
.forml source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1 / NNF
→ IR2 / CNF-DNF
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
```

The DSL is therefore not the verification backend. It is the human-facing entry point of the FORML verification pipeline.

---

## Design Goals

The FORML language aims to provide:

| Goal | Meaning |
|---|---|
| Readability | Properties should be understandable by ML engineers and verification engineers. |
| Formal structure | Every expression must compile into structured AST and IR artifacts. |
| Explicit scope | Each property must define where it is evaluated. |
| Backend independence | The DSL should not encode backend-specific constraints directly. |
| Semantic binding | Implicit and explicit variables must be resolved before IR lowering. |
| Mutation testability | Language artifacts must be suitable for Miova and Hypothesis campaigns. |

---

## Current Language Shape

A FORML program currently contains:

```text
header
body
```

The header declares at least:

```forml
model := "model.joblib"
target := prediction
```

The body contains one or more property sections:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

A property has:

| Element | Role |
|---|---|
| Property type | Describes the verification intent, such as `ROBUSTNESS`, `BOUND`, `FAIRNESS`. |
| Scope | Defines where the property is evaluated, such as `at`, `check_at`, `pairwise`, or `forall`. |
| Assertion | Defines what must hold in that scope. |
| Optional backend | Suggests or selects a verification backend. |

---

## Language vs Semantics

The FORML language defines syntax. The semantic layer defines meaning.

For example:

```forml
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
.forml source
+ ModelSchema
→ schema-aware semantic validation
→ model-aware constraints
→ backend-ready verification query
```

This means the language is only one side of the end-to-end verification problem. The other side is the model representation.

---

## Relationship with Miova and Hypothesis

The FORML language should be testable through:

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
| Header syntax | Implemented / stabilizing | `model`, `target`, optional `dataset`, optional variables. |
| Property sections | Implemented / stabilizing | Property type, scope, implication, assertion, optional backend. |
| Scopes | Implemented / stabilizing | `at`, `check_at`, `pairwise`, quantifiers. |
| Assertions | Implemented / needs cleanup | Comparison, boolean operators, problem predicates. |
| Logic casing | Needs stabilization | Grammar currently mixes lowercase tokens and uppercase literal operators. |
| Vocabulary enums | Needs normalization | Some enum/string boundaries should be stabilized. |
| Backend syntax | Implemented / stabilizing | `using z3`, `using ERAN`, etc. |
| Model-aware validation | Planned / critical | Requires ModelSchema integration. |

---

## Related Documents

- [Grammar](grammar.md)
- [Vocabulary](vocabulary.md)
- [Syntax](syntax.md)
- [Properties](properties.md)
- [Scopes](scopes.md)
- [Assertions](assertions.md)
- [Backends Syntax](backends.md)
- [Examples](examples.md)
