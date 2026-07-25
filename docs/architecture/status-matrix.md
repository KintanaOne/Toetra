# Toetra V1 implementation status

> Status date: 2026-07-26
> Release candidate: `1.0.0rc3`

| Layer | Status | Public guarantee |
|---|---|---|
| Language/AST | implemented | typed output observables, domains, points, anchors |
| Semantics/IR | implemented | binding, IR1 intent, model-semantic lowering, IR2 |
| ModelBridge | implemented | `LinearRegression` and direct binary `LogisticRegression` |
| Numeric compatibility | implemented | rule registry, directed logit intervals, conclusion policy |
| Z3 | implemented | regression, label, probability-order, pairwise-label routes |
| Runtime/reporting | implemented | public `verify`, JSON v6, text/HTML/Jupyter, records |
| Provenance/replay | implemented | stable Decimal fingerprints and concrete model observation |
| Release engineering | implemented | reproducible dist, clean-install route probe, review bundle |

Deferred work includes multiclass models, wrappers/custom thresholds, symbolic
preprocessing, nonlinear model families, categorical backend reasoning,
alternating quantifiers, bit-exact floating-point proofs, and non-Z3 built-ins.
