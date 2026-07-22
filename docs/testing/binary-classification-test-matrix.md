# Binary Classification Acceptance Test Matrix

> Status: Normative acceptance matrix — public `1.0.0rc2` route
> Scope: typed outputs, declarative observables, logistic semantic lowering, ModelBridge, Z3, reporting, replay, release

## Purpose

This matrix gives the Patch 21 tests stable identifiers. Patch descriptions,
test names, parametrization IDs, or comments must reference these IDs so that
cross-layer coverage can be audited.

Parser acceptance alone never counts as classification support. Public support
requires all release-gate groups through `REL-BC-*`.

## P21.0 — Specification contract

| ID | Requirement |
|---|---|
| `DOC-BC-001` | ADR-0023, ADR-0024, and ADR-0025 exist and are marked accepted target. |
| `DOC-BC-002` | The three classification contracts exist and are linked from contract navigation. |
| `DOC-BC-003` | The language page exposes `label` and `probability(label)` but no public logit/score observable. |
| `DOC-BC-004` | Native threshold `0.5`, strict positive boundary, and negative equality boundary are normative. |
| `DOC-BC-005` | Property threshold and native decision threshold are defined separately. |
| `DOC-BC-006` | Direct fitted binary `LogisticRegression` is the first route; wrappers and multiclass are explicitly deferred. |
| `DOC-BC-007` | `1.0.0rc1` and ADR-0022 remain unchanged as the current public profile. |
| `DOC-BC-008` | MkDocs navigation and all local specification links are valid. |

## P21.1 — Typed output schema

| ID | Requirement |
|---|---|
| `SCH-OUT-001` | Scalar regression output schema is deterministic and backward compatible. |
| `SCH-OUT-002` | Binary classification schema records two canonical labels. |
| `SCH-OUT-003` | Available observables are explicit, not inferred from free-form metadata. |
| `SCH-OUT-004` | Output schema contributes deterministically to provenance and fingerprints. |
| `SCH-OUT-005` | Temporary target-name aliases project from the new output source of truth. |
| `SCH-OUT-006` | Invalid or non-serializable label schemas are rejected structurally. |

## P21.2 — Parser and AST observables

| ID | Requirement |
|---|---|
| `PAR-OBS-001` | Parse `target[x0].label`. |
| `PAR-OBS-002` | Parse `target[x0].probability("approved")`. |
| `PAR-OBS-003` | Parse unindexed forms when syntactically legal. |
| `PAR-OBS-004` | Reject missing or multiple probability arguments. |
| `PAR-OBS-005` | Do not accept public `.logit`, `.score`, `.predict_proba`, or `.classes_` forms. |
| `AST-OBS-001` | Represent output-port reference separately from scalar observable projection. |
| `AST-OBS-002` | Preserve point index, observable kind, label literal, and source provenance. |
| `AST-OBS-003` | Existing scalar target AST fixtures remain compatible. |

## P21.3 — Semantic binding and typing

| ID | Requirement |
|---|---|
| `SEM-OBS-001` | Bind label observable to a classification output and point. |
| `SEM-OBS-002` | Bind probability observable to a known canonical label. |
| `SEM-OBS-003` | Reject unknown or wrong-typed labels. |
| `SEM-OBS-004` | Reject bare classification target as ambiguous. |
| `SEM-OBS-005` | Retain bare scalar target for regression. |
| `SEM-OBS-006` | Reject arithmetic and ordering on predicted labels. |
| `SEM-OBS-007` | Reject classification observables on regression outputs. |
| `SEM-OBS-008` | Reuse one evaluation identity for multiple observables at the same point. |

## P21.4 — IR1 evaluation and observables

> Implementation status: complete; covered by unit, integration, NNF, pretty, and golden tests.

| ID | Requirement |
|---|---|
| `IR1-OBS-001` | IR1 preserves observable kind and resolved label. |
| `IR1-OBS-002` | Evaluation identity excludes observable kind and label argument. |
| `IR1-OBS-003` | Distinct points produce distinct evaluation identities. |
| `IR1-OBS-004` | NNF processing preserves observable atoms and polarity. |
| `IR1-OBS-005` | IR1 pretty and golden artifacts remain deterministic. |

## P21.5 — Model semantic lowering

| ID | Requirement |
|---|---|
| `LOW-LBL-001` | Positive-label equality lowers to oriented decision value `> 0`. |
| `LOW-LBL-002` | Negative-label equality lowers to oriented decision value `<= 0`. |
| `LOW-LBL-003` | Inequality preserves exact complement and strictness. |
| `LOW-LBL-004` | Label orientation is independent from user label spelling. |
| `LOW-LBL-005` | Boundary value zero resolves to the negative label. |
| `LOW-EVD-001` | Every rewrite emits deterministic lowering evidence. |
| `LOW-EVD-002` | Source observable survives alongside the canonical constraint. |
| `LOW-EVD-003` | Missing model semantics is rejected before backend routing. |
| `ARCH-SEP-001` | Lowered IR contains no sklearn API object. |
| `ARCH-SEP-002` | Backend translator contains no label or probability semantics. |

## P21.6 — sklearn LogisticRegression bridge

| ID | Requirement |
|---|---|
| `MB-LR-001` | Accept direct fitted binary `LogisticRegression`. |
| `MB-LR-002` | Reject unfitted estimator. |
| `MB-LR-003` | Reject multiclass estimator. |
| `MB-LR-004` | Reject threshold, calibration, pipeline, and custom wrappers. |
| `MB-LR-005` | Extract finite coefficients, intercept, feature order, and labels. |
| `MB-LR-006` | Encoded latent affine value matches `decision_function` over generated finite points. |
| `MB-LR-007` | Native threshold provenance records profile-derived `0.5`/`0`, not a learned attribute. |
| `MB-LR-008` | Existing `LinearRegression` route remains unchanged. |

## P21.7 — Z3 label route

> Implementation status: complete; covered by translator, routing, reporting-role, compatibility, and end-to-end execution tests.

| ID | Requirement |
|---|---|
| `Z3-LBL-001` | Translate canonical latent affine constraints without classification-specific backend logic. |
| `Z3-LBL-002` | Produce `PROVED` for a valid universal label property. |
| `Z3-LBL-003` | Produce and decode a counterexample for a false universal label property. |
| `Z3-LBL-004` | Produce `WITNESS` and `NO_WITNESS` for existential properties. |
| `Z3-LBL-005` | Handle the exact zero boundary consistently. |
| `Z3-LBL-006` | Keep latent symbols distinct across points. |

## P21.8 — Probability threshold lowering

> Implementation status: complete after P21.8.1 soundness correction; covered
> by certified interval, polarity, compatibility-policy, differential sklearn,
> generated-matrix, and Z3 end-to-end tests.

| ID | Requirement |
|---|---|
| `LOW-PROB-001` | Threshold `0.5` lowers exactly to the zero boundary. |
| `LOW-PROB-002` | Order comparisons preserve strictness through monotonic lowering. |
| `LOW-PROB-003` | Negative-label probability uses correct orientation. |
| `LOW-PROB-004` | General thresholds use qualified rational bounds, not silent host floats. |
| `LOW-PROB-005` | Thresholds zero/one and equality operators are rejected initially. |
| `LOW-PROB-006` | `logit(p)` is enclosed from independent `ln(p)` and `ln(1-p)` intervals with directed subtraction. |
| `LOW-PROB-007` | The `p = 0.7` rounded-ratio regression case remains enclosed. |
| `LOW-PROB-008` | Published precision, working precision, and guard digits are deterministic and recorded. |
| `LOW-PROB-009` | Long decimal source literals expand working precision without losing their source spelling. |
| `COMP-PROB-001` | Compatibility class and permitted conclusions are deterministic. |
| `COMP-PROB-002` | Approximation uncertainty cannot yield an unsound stronger result. |
| `COMP-PROB-003` | Lowered and concrete `predict_proba` behavior agree outside declared uncertainty. |

## P21.9 — Reporting and replay

> Implementation status: complete; covered by source-intent reporting, additive JSON v5, text/HTML rendering, sklearn observation, mismatch detection, concrete property reevaluation, and multi-point replay tests.

| ID | Requirement |
|---|---|
| `REP-BC-001` | Report preserves source label/probability intent. |
| `REP-BC-002` | Native threshold and property threshold are distinct fields. |
| `REP-BC-003` | Report may expose latent value as technical evidence, never as requested output. |
| `REP-BC-004` | Report includes reconstructed probabilities, predicted label, margin, and compatibility. |
| `REP-BC-005` | JSON schema evolution is explicit and historical fixtures remain readable. |
| `RPL-BC-001` | Replay compares labels exactly. |
| `RPL-BC-002` | Replay compares probabilities and latent values under declared tolerances. |
| `RPL-BC-003` | Generic replay uses a model-observer protocol, not estimator type checks. |
| `RPL-BC-004` | Multi-point classification evidence is replayed per evaluation. |

## P21.10 — Pairwise classification — complete

| ID | Requirement |
|---|---|
| `PAIR-BC-001` | Explicit equality of two predicted labels lowers soundly. |
| `PAIR-BC-002` | Equality is symmetric and preserves zero-boundary policy. |
| `PAIR-BC-003` | `CLASSIFICATION.EQUAL()` is equivalent to the explicit form. |
| `PAIR-BC-004` | Sugar rejects any context without exactly two eligible evaluations. |
| `PAIR-BC-005` | Pairwise proof and counterexample execute end to end. |

## P21.11 — Release candidate — complete

| ID | Requirement |
|---|---|
| `REL-BC-001` | Documentation, implementation, generated matrices, and public facade agree. |
| `REL-BC-002` | Real binary-classification demo executes from source checkout. |
| `REL-BC-003` | Wheel clean-install executes label and probability properties. |
| `REL-BC-004` | Text, JSON, HTML, Jupyter, and replay artifacts are produced. |
| `REL-BC-005` | All `LinearRegression` public fixtures remain green. |
| `REL-BC-006` | ADR-0022/public profile is amended only at this gate for `1.0.0rc2`. |
| `REL-BC-007` | `make ci`, `make release-check`, and review-bundle checks are green. |

## Cross-patch regression rule

Every implementation patch after P21.0 must include:

1. unit tests for its local responsibility;
2. contract tests for each changed boundary;
3. negative tests proving failure ownership;
4. `LinearRegression` non-regression coverage;
5. one golden or end-to-end case as soon as the feature reaches that layer.
