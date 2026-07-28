# Implementation status matrix

> **Status date:** 2026-07-28
>
> **Release candidate:** `1.0.0rc3`
>
> **Authority:** the [public V1 profile](../public-v1-profile.md) controls
> executable support

This matrix distinguishes three different statements that older architecture
pages sometimes conflated:

- **implemented**: code and tests exist inside the repository;
- **built-in V1**: the default installed runtime uses the component;
- **public V1**: the complete route is guaranteed by the public profile.

Infrastructure alone is not a public route.

## End-to-end layers

| Layer | Implemented | Built-in V1 | Public V1 guarantee |
|---|---|---|---|
| `.toetra` parser and typed AST | yes | yes | supported syntax subject to the public profile |
| semantic binding and typing | yes | yes | points, anchors, domains, observables, and homogeneous binders used by supported routes |
| IR1 translation | yes | yes | internal only |
| model-semantic lowering | yes | yes | regression identity plus initial binary-logistic label/probability semantics |
| NNF normalization | yes | yes | internal only |
| IR2 NNF/CNF/DNF | yes | yes | internal only; selected under guardrails |
| typed domain, anchor, and model assumptions | yes | yes | assumptions required by supported routes |
| capability requirements and routing | yes | yes | fail-closed Z3 selection |
| numeric compatibility policy | yes | yes | exact-real affine abstraction and directed logistic-threshold bounds |
| backend execution policy | yes | yes | timeout and supported Z3 execution controls |
| reports and JSON v6 | yes | yes | text, HTML, Jupyter, records/DataFrame, JSON |
| provenance fingerprints | yes | yes | specification, artifacts, compiler, route, and verification context |
| concrete replay | yes | yes | supported scalar and binary-classification observations |

## Model routes

| Route | Infrastructure state | Public V1 |
|---|---|---|
| sklearn fitted single-output `LinearRegression` | schema, affine encoder, Z3 translation, reporting, replay | supported |
| direct fitted binary sklearn `LogisticRegression` | schema, oriented-decision encoder, semantic profiles, Z3, reporting, replay | supported |
| XGBoost detection/introspection | partial internal infrastructure | not supported end to end |
| trees and ensembles | no complete encoder/backend route | excluded |
| neural networks | no complete encoder/backend route | excluded |
| sklearn `Pipeline` reconstruction | no symbolic preprocessing route | excluded |
| multiclass or multi-output | no complete semantics/report/replay route | excluded |
| wrapper/custom-threshold classifiers | native decision policy not frozen | excluded |

## Language and logical forms

| Capability | Implemented | Public V1 boundary |
|---|---|---|
| numeric feature comparisons and affine arithmetic | yes | supported |
| Boolean `AND`, `OR`, `NOT`, implication | yes | supported within executable routes |
| typed numeric intervals and finite sets | yes | supported |
| inline and referenced points/anchors | yes | supported |
| homogeneous `forall` bindings | yes | supported through refutation semantics |
| homogeneous `exists` bindings | yes | supported through witness semantics |
| alternating quantifiers | detected and rejected | excluded |
| regression `target[point]` | yes | supported |
| classification `.label` | yes | supported for direct binary logistic models |
| classification `.probability(label)` ordering | yes | thresholds strictly inside `(0, 1)` |
| pairwise binary-label equality/inequality | yes | supported |
| categorical/string backend reasoning | syntax/type infrastructure only | excluded |
| nonlinear symbolic arithmetic | requirement detection only | excluded |

## Backend and execution

| Capability | Z3 implementation | Public V1 |
|---|---|---|
| exact-real affine numeric encoding | yes | supported with compatibility evidence |
| NNF, CNF, and DNF input forms | yes | internal route detail |
| domain and model assumptions | yes | supported |
| point-specific solver identities and reverse mapping | yes | supported |
| universal refutation / existential witness | yes | supported |
| assumption consistency diagnostics | yes | reported when budget permits |
| timeout and cancellation | yes | supported by internal execution-policy hook |
| deterministic seed and backend units | yes where declared by capability profile | internal advanced hook |
| memory ceiling | not claimed by default Z3 profile unless enforceable | fail-closed |
| ERAN or another built-in backend | no | excluded |
| multi-backend voting/comparison | no | post-V1 direction |

## Public versus private surfaces

| Surface | Stability |
|---|---|
| nine names exported by `toetra.__all__` | public V1 |
| `toetra.examples` installed resource helper | packaged helper, documented separately |
| `toetra._compiler`, `toetra._models`, `toetra._backends` | private implementation |
| `toetra._runtime`, `toetra._reporting`, `toetra._provenance` | private implementation |
| registry, encoder, policy, and context injection keywords accepted by `verify(...)` | advanced development hooks; their private types are not public API |

## Explicit post-V1 direction

The following topics may guide extension work but are not incomplete pieces of
the V1 route:

- additional model families and framework adapters;
- symbolic preprocessing and pipeline reconstruction;
- non-Z3 backends;
- categorical and tensor reasoning;
- alternating or native backend quantifiers;
- bit-exact floating-point semantics;
- runtime monitoring and remote/distributed orchestration.

A route becomes public only after the extension rule in
[`public-v1-profile.md`](../public-v1-profile.md#extension-rule) is satisfied
across schema, semantics, encoding, capabilities, numeric policy, execution,
reporting, replay, tests, documentation, and release validation.
