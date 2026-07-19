# FORML V1 implementation status

> Status date: 2026-07-19  
> Release candidate: `1.0.0rc1`

## End-to-end implementation

| Layer | V1 status | Public guarantee |
|---|---|---|
| EBNF and generated Lark | implemented | EBNF is the language source of truth and generated grammar is checked in CI. |
| Parser and AST | implemented | Structured properties, expressions, domains, points, anchors, and source spans. |
| Semantic layer | implemented | Binding, types, point visibility, anchors, evaluations, and early capability requirements. |
| IR1 and IR2 | implemented | Logical normalization, assumptions, requirements, verification semantics, and normal forms. |
| ModelBridge | implemented for V1 profile | One affine equation per requested sklearn `LinearRegression` evaluation. |
| Numeric compatibility | implemented | Generic rule registry, conclusion policy, generated support and guarantee matrices. |
| Backend routing | implemented | Structural, numeric, and execution-policy compatibility checked before execution. |
| Z3 execution | implemented | SAT/UNSAT/UNKNOWN, timeout/resource/cancellation evidence, model assignments. |
| Runtime | implemented | Public `verify`, anchor resolution, sessions, findings, artifacts, exit codes. |
| Reporting | implemented | Text, HTML, Jupyter, records/DataFrame, frozen JSON v5. |
| Provenance | implemented | Content fingerprints, software/compiler identity, complete/partial status. |
| Replay | implemented | Referenced points evaluated against the original estimator. |
| Release engineering | implemented | Non-mutating CI, reproducible distributions, clean installation, review bundles. |

## Public V1 profile

See [Public V1 profile](../public-v1-profile.md). It is narrower than the complete
language vocabulary and extension architecture.

## Deferred

Additional built-in model families, classifiers, preprocessing reconstruction,
categorical reasoning, alternating quantifier execution, floating-point-exact
proofs, and non-Z3 built-in backends are post-V1 work.
