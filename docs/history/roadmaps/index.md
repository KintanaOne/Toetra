# Project history

> **Status:** Chronological record through the current `1.0.0rc3` evaluation
> candidate

This section explains how Toetra reached its current public profile. It records
delivered capabilities and engineering decisions; it does not define current
support or future commitments. For those, use the
[public V1 profile](../../public-v1-profile.md) and the
[implementation roadmap](../../roadmap/implementation-roadmap.md).

## From architecture to public evaluation

| Period | Milestone | Outcome |
|---|---|---|
| Early V1 development | [V1 foundations](v1-implementation-roadmap.md) | Layered compiler, model bridge, Z3 backend, reporting, replay, and release engineering established |
| Before `1.0.0rc1` | [Point-based semantics](point-binding-evaluation-implementation-roadmap.md) | First-class points, anchors, quantified bindings, indexed evaluations, and multi-point evidence delivered |
| 2026-07-19 | `1.0.0rc1` | First end-to-end public regression route for sklearn `LinearRegression` |
| 2026-07-22 | [Binary classification](binary-classification-implementation-roadmap.md) and `1.0.0rc2` | Direct binary sklearn `LogisticRegression`, label and probability observables, reporting, and replay added |
| 2026-07-26 | [Canonical Toetra identity](toetra-identity-migration-roadmap.md) and `1.0.0rc3` | Distribution, namespace, language, extension, reports, and documentation adopted the Toetra identity |
| Late July 2026 | [Repository structure](repository-final-polish-roadmap.md) | Source, tests, demos, scripts, and internal package boundaries consolidated |
| Late July 2026 | [Documentation and user experience](documentation-roadmap.md) | Public API, as-built architecture, language reference, diagnostics, reports, and first-use paths aligned |
| Current candidate | Public-evaluation readiness | Reproducible artifacts, licensing, provenance, contribution policy, outside-in checks, and controlled exposure procedure completed |

## What remained stable throughout

Toetra evolved by strengthening one end-to-end verification path before adding
another. Language meaning, model-family semantics, framework integration,
backend execution, numeric compatibility, reporting, and replay remained
separate responsibilities. A capability entered the public profile only when
all of those layers and their tests agreed.

The detailed reasons behind enduring architectural choices remain in the
[ADRs](../../adr/overview.md), while executable guarantees remain in the
[contracts](../../contracts/overview.md).
