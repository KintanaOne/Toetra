# Model Semantic Lowering Contract

> Status: Implemented — public in `1.0.0rc2`
> Normative ADR: [ADR-0024](../adr/ADR-0024-model-semantic-lowering.md)
> Scope: IR1 observables, model-family semantics, canonical constraints, compatibility, provenance

## Purpose

This contract defines the only boundary at which a public output observable may
be rewritten into model-family-specific mathematical constraints.

## Input

The lowering step receives:

- schema-validated IR1 preserving the source observable;
- the model output schema;
- a deterministic model semantic profile;
- any model quantities materialized by the ModelBridge encoder;
- the requested comparison and logical context;
- the active numeric compatibility policy.

## Output

The lowering step returns:

1. canonical logical or scalar constraints consumable by normalization and
   capability routing;
2. all requirements introduced by the rewrite;
3. structured lowering evidence;
4. a numeric compatibility classification and permitted conclusions;
5. a structured rejection when no defined rewrite exists.

## Ownership rule

| Concern | Owning layer |
|---|---|
| Syntax of `label` or `probability(label)` | DSL/AST |
| Label existence and observable type | semantic layer |
| Meaning of an observable for a mathematical model family | model semantic profile |
| Coefficients and equations of a concrete model | ModelBridge encoder |
| Exactness or conservativeness of numeric materialization | compatibility registry/policy |
| Translation of canonical constraints | backend |
| Explanation of the rewrite | provenance/reporting |

A framework adapter may select a model semantic profile, but it must not redefine
the profile's meaning privately.

## P21.5 implemented surface

Patch 21.5 implements the first concrete slice of this contract:

- semantic profiles are selected by framework-neutral `model_family`;
- the initial family is `binary_logistic_affine_classifier`;
- `predicted_label == literal` and `predicted_label != literal` are lowered exactly;
- the generated internal quantity is an `oriented_decision_value`;
- the positive label uses the strict boundary `> 0`;
- the negative label, including equality at zero, uses `<= 0`;
- deterministic `LoweringEvidence` is attached to the resulting IR2 task;
- a missing profile or a generic IR2 route without model semantics is rejected;
- backends must opt in explicitly to model-semantic quantities.

P21.6 materializes the concrete affine decision equation for direct binary
`LogisticRegression`, and P21.7 translates the resulting canonical quantity and
equation through Z3. P21.8 implements order comparisons on
`probability(label)` with exact lowering at `0.5` and outward directed decimal
bounds for other thresholds. No public DSL syntax exposes the internal decision
quantity.

## P21.8 probability lowering invariants

- accepted thresholds are finite numeric literals strictly inside `(0, 1)`;
- only `<`, `<=`, `>`, and `>=` are initially supported;
- positive-label probability is monotone in the oriented decision value;
- negative-label probability reverses the comparison orientation;
- `0.5` maps exactly to the decision threshold `0`;
- every other threshold retains an outward lower and upper decimal bound;
- bounds are constructed from independent intervals for `ln(p)` and
  `ln(1 - p)`, never from a previously rounded quotient;
- final bounds publish 50 significant decimal digits;
- working precision uses at least 20 guard digits and expands for long source
  literals;
- probability-threshold evidence uses transformation version `2`;
- logical polarity controls which bound preserves a global property
  under-approximation;
- approximate lowerings permit universal proofs and existential witnesses only;
- unsupported backend conclusions are changed to `UNKNOWN` by semantic-lowering
  policy;
- approximate probability predicates in scope restrictions are rejected before
  backend routing.

## P21.10 pairwise predicted-label lowering invariants

Explicit predicted-label equality lowers to `(z0 > 0 and z1 > 0) or (z0 <= 0 and z1 <= 0)`. Inequality lowers to the two opposite-region branches. The lowering is exact, symmetric, and retains both evaluation identities.

`CLASSIFICATION.EQUAL()` is semantic sugar, valid only with exactly two visible model-input points. It is lowered before NNF; a supported route never sends residual `ProblemIR` to a backend.

## Lowering evidence invariants

Every non-identity lowering must retain:

| Field | Meaning |
|---|---|
| source intent | the original observable comparison |
| evaluation identity | model, point, and output port |
| observable identity | kind and resolved label |
| profile identifier | stable semantic-family identifier |
| transformation identifier | stable rewrite name/version |
| canonical result | generated constraints before backend translation |
| boundary policy | strict/non-strict decision behavior |
| numeric evidence | exact value or conservative bounds, selected side, published precision, working precision, and guard digits |
| compatibility class | `EXACT`, `SOUND_OVER`, `SOUND_UNDER`, or other registered class |
| permitted conclusions | results that remain valid under the transformation |

Evidence must be deterministic and serializable for provenance fingerprints.

## Ordering relative to logical normalization

A lowering that can generate Boolean structure must occur before the final NNF
and IR2 normal-form selection for that expression.

Example: equality of two binary predicted labels may lower to a disjunction of
two conjunctions. Normalizing first and lowering later would make polarity and
negation handling ambiguous.

## Numeric rules

- Identity affine rewrites may remain exact when all literals are exact.
- A mathematical equivalence involving a transcendental function does not imply
  that its finite serialized threshold is exact.
- Binary floating-point host calculations must not enter the proof silently.
- Conservative bounds must record their direction, published precision, working
  precision, and guard digits.
- Logistic thresholds must use interval evaluation of `ln(p) - ln(1 - p)` with
  directed subtraction and outward final rounding.
- Computing the logarithm of a rounded odds ratio is not a valid enclosure
  procedure for this contract.
- A backend result inside an approximation uncertainty region cannot be promoted
  to a stronger public conclusion.

## Failure ownership

The model semantic lowering boundary owns diagnostics for:

- observable unsupported by the selected model family;
- comparison unsupported by the initial profile;
- missing model quantity required by a rewrite;
- unsupported custom decision policy;
- unsupported threshold edge case;
- numeric policy unable to preserve the requested conclusion.

These failures must occur before backend translation.

## Backend-independence invariant

Canonical constraints and lowering evidence must not contain backend API objects.
The same lowered task may be routed to any backend declaring the required
capabilities and compatible numeric profile.

## Non-goals

- defining one universal classification encoding;
- allowing backends to call model framework methods;
- forcing all models to expose probabilities;
- hiding approximate lowerings behind exact-looking decimal constants;
- changing the public result taxonomy.

## Mutation and testing hooks

Required stable test groups are:

- `LOW-LBL-*` for label rewrites;
- `LOW-PROB-*` for probability rewrites;
- `LOW-EVD-*` for lowering evidence;
- `COMP-PROB-*` for numeric compatibility;
- `ARCH-SEP-*` for framework/backend separation.
