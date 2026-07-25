# ADR-0024 — Lower Declarative Output Observables Through Model-Family Semantics

> Status: Accepted — public in `1.0.0rc2`; probability-threshold soundness amended by P21.8.1
> Date: 2026-07-20
> Scope: semantic IR, ModelBridge, IR2 construction, numeric compatibility, backend boundary, provenance

## Context

A declarative property can refer to a value that is not natively represented in
the arithmetic fragment of a backend. For example, a user may ask whether a
binary classifier predicts a named label or assigns that label a probability of
at least `0.80`.

A logistic classifier can implement those intentions through a latent affine
decision value, but that is a property of one mathematical model family. It is
not the universal definition of classification, and it is not the responsibility
of Z3 or any other backend to invent that meaning.

Without an explicit lowering boundary, the implementation could accidentally:

- erase the user's original intent too early;
- define classification in sklearn-specific code;
- make the Z3 translator aware of labels and probabilities;
- hide numeric approximations introduced by probability thresholds;
- produce reports that show only an internal equation rather than the requested
  property.

## Decision

Toetra will introduce an explicit **model-semantic lowering** step between the
declarative observable representation and backend-oriented verification
constraints.

The conceptual pipeline is:

```text
DSL declarative property
→ schema-aware semantic representation
→ IR1 preserving output observables
→ model-family semantic lowering
→ normalized verification IR
→ capability routing
→ backend query
```

### Ownership

The responsibilities are divided as follows:

| Layer | Responsibility |
|---|---|
| DSL and AST | Preserve declarative output syntax. |
| Semantic layer | Bind points, output ports, labels, and observable types. |
| IR1 | Preserve the user-visible observable and comparison. |
| Model semantic profile | Define valid rewrites from observables to canonical model quantities. |
| ModelBridge encoder | Materialize the mathematical constraints for those quantities. |
| Numeric compatibility | Qualify exactness, over-approximation, under-approximation, and permitted conclusions. |
| Backend | Translate only the canonical constraints and declared assumptions it receives. |
| Reporting and provenance | Preserve both the source intention and the executed rewrite. |

No backend defines the meaning of a label, a probability, or a model-family
decision rule.

### Lowering evidence

Every non-identity rewrite must produce structured `LoweringEvidence` containing
at least:

- the source observable expression;
- the resolved output and point identities;
- the model semantic profile identifier;
- the transformation identifier and version;
- the canonical expression or constraint produced;
- the boundary policy used for strict or non-strict decisions;
- the numeric compatibility classification;
- any approximation interval or precision metadata;
- the conclusions permitted from that lowering.

The exact Python representation is deferred to Patch 21.5. The information is a
normative contract.

### Information-preservation rule

The canonical constraint is a compilation artifact. It must not replace the
source intention in IR1, provenance, or the final report.

A report may explain an internal decision value, but must continue to state that
the verified property concerned a label or a class probability estimate.

### Numeric rule

An algebraically valid rewrite is not automatically numerically exact in its
materialized form. If a transformation introduces a non-rational threshold, its
representation must follow ADR-0018:

- no silent binary-float literal insertion;
- exact cases are classified `EXACT`;
- conservative bounds are classified `SOUND_OVER` or `SOUND_UNDER` as
  appropriate;
- inconclusive boundary regions produce refinement, replay, or `UNKNOWN` rather
  than an unsound stronger conclusion.

### P21.8 directed probability threshold policy

For the binary logistic profile, a public order comparison on
`probability(label)` is first converted to the corresponding comparison on the
oriented decision value. The exact threshold is `logit(p)` for the positive
label and `-logit(p)` for the negative label.

The native threshold `p = 0.5` lowers exactly to zero. For every other accepted
threshold, Toetra computes an outward decimal interval enclosing the exact logit
at a declared precision. The selected bound depends on:

- the comparison direction;
- the requested label orientation;
- whether the atom appears under positive or negative logical polarity.

The complete lowered property is constructed as an under-approximation of the
source property's satisfying set. Consequently, without a later refinement or
concrete replay, an approximate probability lowering permits:

- a universal proof;
- an existential witness.

A universal counterexample or existential no-witness produced only against the
directed bound is downgraded to `UNKNOWN`. The lowering evidence records both
bounds, the selected side, precision, logical polarity, and permitted
conclusions.

Non-exact probability thresholds in scope restrictions remain deferred because
approximating an admissible domain requires a goal-specific assumption policy.

### Probability-threshold materialization amendment (P21.8.1)

A probability threshold must be lowered from its exact decimal source spelling.
For non-native thresholds, the semantic profile constructs an interval for
`logit(p)` from separate intervals for `ln(p)` and `ln(1 - p)`. It must not first
round `p / (1 - p)` and then enclose the logarithm of that rounded quotient.

The profile publishes 50 significant decimal digits and computes with at least
20 guard digits. If the source literal is longer, working precision expands to
retain it. Lowering evidence records both precision levels and the guard policy.
The probability-threshold transformation version is incremented to `2` so
provenance distinguishes this certified construction from the original P21.8
rounded-ratio materialization.
The precision constants may narrow or widen the uncertainty region, but only
outward rounding and interval arithmetic justify the soundness classification.

### Failure ownership

Unsupported observables, unsupported model-family rewrites, and unsupported
numeric policies must be rejected before backend translation. The backend must
never be the first component to discover that a public classification intention
has no defined lowering.

## Rationale

The semantic model family is the narrowest layer that knows both:

- what the user-visible observable means for that family; and
- which mathematical representation can preserve it.

This keeps Toetra independent from frameworks and backends while making every
rewrite auditable.

## Consequences

- IR1 remains closer to the DSL than the executable IR.
- The IR2 build path gains a schema/model-semantic dependency for observable
  properties.
- Normalization order must account for lowerings that produce Boolean structure.
- Compatibility requirements must describe semantic transformations, not only
  backend operator support.
- Reports and replay gain a first-class lowering trace.

## Non-goals

This ADR does not:

- define the binary logistic equations themselves;
- require every model family to expose probabilities;
- expose internal quantities in the DSL;
- require Z3 as the lowering target;
- permit unqualified approximations;
- change the current public release profile.

## Alternatives considered

### Lower directly inside the sklearn encoder

Rejected because the meaning would become framework-specific and difficult to
reuse for another framework implementing the same mathematical family.

### Lower inside the Z3 translator

Rejected because it would make Z3 the semantic authority and prevent another
backend from consuming the same canonical contract.

### Convert output observables during parsing

Rejected because the parser has neither a model schema nor a model-family
semantic profile.

## Impact on Toetra

This ADR extends ADR-0010, ADR-0018, and ADR-0020 with a model-semantic rewrite
boundary. Existing affine regression properties are identity lowerings and remain
compatible.

## P21.9 trace and replay amendment

IR2 now retains the original pre-lowering IR1 specification alongside the
canonical lowered formula. User-facing reports and concrete replay evaluate the
original observable intention, while `LoweringEvidence` explains the canonical
constraint used by the backend.

A displayed probability reconstructed from a formal decision quantity is
explicitly presentation evidence computed at 50 significant decimal digits. It
is not substituted for the certified threshold interval or used to strengthen a
verification conclusion.
