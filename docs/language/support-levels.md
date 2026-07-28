# Language support levels

> Status: Current for `1.0.0rc3`
> Scope: Interpretation of every Toetra language reference page
> Audience: users, compiler contributors, extension authors, and reviewers

## Why Toetra uses three levels

A source fragment is not supported merely because the parser accepts it.
Toetra evaluates a specification through three distinct gates:

| Gate | Question | Owner | Success establishes |
|---|---|---|---|
| Syntax | Does the source parse? | grammar, parser, and AST builder | A structurally complete AST |
| Semantics | Does the AST have an accepted meaning in this context? | semantic validation and model schema | Exact bindings, types, point evaluations, and requirements |
| Public execution | Is there a released route able to verify it? | public V1 profile, model encoder, router, and backend | A supported end-to-end verification request |

The gates are cumulative:

```text
publicly executable
    implies semantically valid
    implies syntactically valid
```

The reverse implications do not hold. This distinction is part of the V1
contract, not an implementation detail.

## Sources of authority

When two pages appear to differ, use this order:

1. [Public V1 profile](../public-v1-profile.md) for released end-to-end routes.
2. The committed EBNF and generated Lark grammar for accepted source structure.
3. Accepted contracts and ADRs for language meaning.
4. This language reference for user-facing explanation.
5. Historical roadmaps only for design history.

Parser acceptance must never be used to infer public support. Likewise, an
implemented internal encoder is not public until the public profile names its
complete route.

## Current support map

| Construct | Syntax | Semantic meaning | Public V1 execution |
|---|---|---|---|
| `model` and `target` declarations | accepted | required identities | only routes named by the public profile |
| optional `dataset` declaration | accepted | path metadata and possible anchor source | subject to the public runtime route |
| scalar specification constants | accepted | immutable typed values | supported when their use stays inside the selected route |
| inline and referenced anchors | accepted | concrete point identities | supported by the numeric-affine routes |
| `forall` and `exists` points | accepted | ordered point binders | homogeneous chains only |
| alternating quantifiers | accepted | represented without losing order | capability-rejected in V1 |
| numeric interval domains | accepted | typed domain assumptions | supported by the numeric-affine routes |
| finite numeric sets | accepted | typed discrete assumptions | supported where the Z3 numeric profile can encode them |
| symbolic or string finite sets | accepted | categorical values | outside the built-in Z3 V1 profile |
| scalar comparisons and Boolean logic | accepted | typed predicates | supported when every scalar requirement is supported |
| affine arithmetic | accepted | classified as affine | supported by the numeric-affine routes |
| symbolic multiplication or division | accepted | classified without approximation | capability-rejected by the built-in Z3 V1 route |
| regression `target[point]` | accepted | scalar model evaluation | public for fitted single-output `LinearRegression` |
| `.label` and `.probability(label)` | accepted | classification observables | public for direct fitted binary `LogisticRegression` |
| `CLASSIFICATION.EQUAL()` | accepted | two-point predicted-label equality | public for exactly two visible binary evaluations |
| `Z3` or `z3` | accepted | explicit required backend | public built-in backend |
| ERAN, zonotope, or box names | reserved syntax | rejected as V1 backends | not supported |

This table summarizes built-in support. It does not widen the exact framework,
model, numeric, reporting, or replay constraints in the public profile.

## Worked boundary examples

### Syntax, semantics, and public execution

This shape belongs to the public regression route when the supplied model and
feature schema satisfy the public profile:

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

Parsing alone does not prove that `linear.joblib` is a fitted supported model;
loading, schema validation, encoding, routing, and execution still occur.

### Valid language, unsupported built-in route

```toetra
model := "model.joblib"
target := score

[LOGIC]:
forall applicant
with domain(
    applicant.region: {EU, US}
)
=> target[applicant] <= 1 using Z3
```

The finite set has accepted categorical meaning when the model schema agrees.
The built-in Z3 V1 profile has no public categorical encoding, so the request
must be rejected at capability routing rather than approximated.

### Parses, but has invalid meaning

```toetra
model := "model.joblib"
target := score

[LOGIC]:
forall applicant
=> other.income >= 0
```

`other.income` is structurally an attribute reference, but `other` is not a
visible point. Exact binding therefore rejects the program during semantic
validation.

### Does not parse

```text
model := "model.joblib"
target := score

[LOGIC]:
forall
=> target <= 1
```

Every quantifier requires at least one explicit point identifier.

## Failure ownership

| Failure | Expected boundary |
|---|---|
| malformed declaration, scope, domain, or assertion | parser or AST builder |
| unknown point, ambiguous shorthand, invalid type, or invalid interval | semantic validation |
| unsupported problem/function combination | semantic validation |
| unsupported arithmetic class, categorical requirement, or quantifier alternation | route qualification |
| unavailable model equation | model encoder |
| unsupported or unregistered backend | semantic validation or route qualification |
| solver translation or execution failure | backend adapter |

A verification result such as `COUNTEREXAMPLE`, `NO_WITNESS`, or `UNKNOWN` is
not a compilation failure. It is an outcome produced after all three gates have
accepted the request.

## Labels used in this reference

Language pages use these labels consistently:

- **Accepted syntax** means the committed grammar and builder represent it.
- **Accepted semantics** means the semantic layer assigns it a defined meaning.
- **V1 executable** means a route in the public V1 profile supports it.
- **Capability-rejected** means it can be valid language but the selected route
  cannot execute it.
- **Reserved syntax** means the parser recognizes it only to preserve vocabulary
  or produce a deliberate diagnostic; it is not a supported feature.
- **Post-V1** describes direction only and never implies present support.

## Review rule

Every new language example must make its intended level clear. A page must not
label an example “supported” unless it identifies the public route that supports
it. P25.5 adds automated checks for the selected canonical snippets; until then,
the grammar, semantic tests, public profile, and release demos remain the
evidence.
