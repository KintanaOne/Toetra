# Binary Classification Implementation Roadmap

> Status: Complete — Patch 21
> Target release: `1.0.0rc2` after all gates
> Public release contract: `1.0.0rc2`

## Implementation progress

| Patch | Status | Implemented result |
|---|---|---|
| P21.0 | Complete | ADRs, contracts, language boundary, test matrix, and roadmap frozen. |
| P21.1 | Complete | Typed output schemas and read-only scalar-target compatibility projections. |
| P21.2 | Complete | Declarative `label` and `probability(label)` syntax plus explicit AST observables. |
| P21.3 | Complete | Schema-aware binding, typing, label validation, observable capability checks, and shared evaluation identity. |
| P21.4 | Complete | IR1 preserves observable kind, canonical label, scalar type, point identity, and shared model evaluation identity. |
| P21.5 | Complete | Framework/backend-neutral predicted-label lowering, exact boundary semantics, evidence, and capability gating. |
| P21.6 | Complete | Direct fitted binary sklearn `LogisticRegression` is introspected, profiled, and encoded as an affine internal decision quantity. |
| P21.7 | Complete | Z3 executes predicted-label properties with point-aware latent quantities. |
| P21.8 / P21.8.1 | Complete | Probability-order properties use certified directed logit intervals. |
| P21.9 | Complete | Reports preserve source intent and replay label, probability, latent quantity, and original property. |
| P21.10 | Complete | Explicit pairwise label equality/inequality and `CLASSIFICATION.EQUAL()` share one exact lowering. |
| P21.11 | Complete | Public contract, release docs, demos, clean-install smoke route, and `1.0.0rc2` metadata finalized. |

P21.11 completes release hardening and ADR-0026 adopts the route in the public `1.0.0rc2` profile.

## Goal

Introduce a framework-neutral declarative binary-classification contract and make
a direct fitted sklearn `LogisticRegression` its first complete implementation.

The work is not considered complete when an estimator can be encoded. It is
complete only when the intention survives DSL, semantic binding, lowering,
verification, reporting, replay, packaging, and public documentation.

## Normative foundations

- [ADR-0023 — Typed Model Outputs and Observables](../adr/ADR-0023-typed-model-outputs-and-observables.md)
- [ADR-0024 — Model Semantic Lowering](../adr/ADR-0024-model-semantic-lowering.md)
- [ADR-0025 — Initial Binary Classification Profile](../adr/ADR-0025-binary-classification-profile.md)
- [Binary Classification Test Matrix](../testing/binary-classification-test-matrix.md)

## Patch sequence

| Patch | Main outcome | Principal debt intentionally retained | Exit gate |
|---|---|---|---|
| P21.0 | Freeze ADRs, contracts, vocabulary, syntax target, test matrix, and roadmap. | No implementation; public rc1 remains regression-only. | `DOC-BC-*` |
| P21.1 | Add typed output schemas and compatibility projections. | Temporary old `target_*` aliases. | `SCH-OUT-*` |
| P21.2 | Add declarative output-observable syntax and AST. | Syntax accepted before semantic execution. | `PAR-OBS-*`, `AST-OBS-*` |
| P21.3 | Bind and type observables against schema. | Some syntactic combinations explicitly rejected. | `SEM-OBS-*` |
| P21.4 | Separate evaluation identity and observable identity in IR1. | Compatibility IR aliases during migration. | `IR1-OBS-*` |
| P21.5 | Add framework/backend-neutral model-semantic lowering and evidence. | Label-literal route first; probability later. | `LOW-LBL-*`, `LOW-EVD-*`, `ARCH-SEP-*` |
| P21.6 | Add direct binary sklearn `LogisticRegression` bridge. | No wrappers, calibration, pipelines, or multiclass. | `MB-LR-*` |
| P21.7 | Execute predicted-label properties through Z3. | Reporting still transitional. | `Z3-LBL-*` |
| P21.8 / P21.8.1 | Execute probability-order properties with certified interval lowering; P21.8.1 corrects rounded-ratio enclosure. | No probability equality, edge thresholds, or arithmetic. | `LOW-PROB-*`, `COMP-PROB-*` |
| P21.9 | Add classification reporting, provenance, and replay. | First concrete observer is sklearn. | `REP-BC-*`, `RPL-BC-*` |
| P21.10 | Add explicit pairwise label equality and define `CLASSIFICATION.EQUAL()` sugar. | No multiclass/top-k/probability-difference relations. | `PAIR-BC-*` — complete |
| P21.11 | Harden, document, package, and publish the `1.0.0rc2` candidate profile. | Deferred features recorded for post-V1 work. | `REL-BC-*` — complete |

## Dependency order

```text
P21.0
  ↓
P21.1 → P21.2
  ↓       ↓
  └──→ P21.3 → P21.4 → P21.5 → P21.6 → P21.7 → P21.8
                                             ↓         ↓
                                             └──→ P21.9 → P21.10 → P21.11
```

P21.6 must not introduce the first semantic definition of labels or probabilities.
It only implements a profile already frozen by P21.0 and represented by P21.1–P21.5.

## Rename and migration policy

Patch 21 must remove scalar-output assumptions without forcing a single big-bang
rename. The implementation should:

1. introduce the output-oriented source of truth;
2. migrate internal consumers patch by patch;
3. keep temporary read-only compatibility projections where needed;
4. prevent new code from depending on the obsolete scalar-target names;
5. retain old scalar-target names as read-only 1.x compatibility aliases and forbid new internal dependencies on them.

Priority review targets include:

```text
TargetRefNode
TargetExpressionIR
ModelEvaluationIR.target_name
ModelEvaluationIdentity.target_name
AffineOutputConstraintIR2
Z3ModelOutputIdentity
target_source_dtype
```

Exact names may change after code review, but the conceptual split in ADR-0023 is
mandatory.

## Public-language boundary

The intended user forms are:

```text
target[x0].label == "approved"
target[x0].probability("approved") >= 0.80
```

No patch may add public syntax for a logit, decision function, generic score,
framework method, class index, affine quantity, or backend variable without a new
ADR.

## Native threshold rule

The initial route uses the direct estimator's recognized standard decision policy:

```text
positive probability > 0.5
or equivalently oriented decision value > 0
```

Equality belongs to the negative label. Custom or tuned thresholds require a
future semantic profile and are rejected in Patch 21.

## Completion definition

Patch 21 is complete only when:

- the DSL is framework- and backend-independent;
- one evaluation can expose several observables without duplication;
- labels are resolved by value, never public class index;
- the zero boundary is exact and tested;
- probability lowering is numerically qualified;
- unsupported models fail before the backend;
- reports retain source intent and explain internal lowering;
- concrete replay covers label, probability, latent evidence, and original property;
- the existing regression route remains compatible;
- a clean-installed wheel passes the complete route;
- the public profile is amended explicitly for `1.0.0rc2`.
