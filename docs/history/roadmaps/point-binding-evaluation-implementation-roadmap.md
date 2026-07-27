# Point Binding and Evaluation Implementation Roadmap

> Status: Completed — Patch 15.1 through 15.12 delivered
> Date: 2026-07
> Scope: Patch 15 — first-class points, anchors, nested binders, restrictions, indexed model evaluations, and multi-point evidence
> Prerequisite: Patch 15-D1 documentation and contract freeze

## Purpose

This roadmap converts the accepted point-binding specification into a sequence of implementation patches that can be integrated while keeping the repository green after every delivery.

The roadmap is subordinate to the following normative sources:

1. ADR-0017 — first-class points and point-indexed evaluations;
2. `language/points-anchors-and-evaluations.md`;
3. `contracts/point-binding-and-evaluation.md`;
4. `testing/point-binding-evaluation-test-matrix.md`.

If this roadmap conflicts with one of those documents, the normative document wins and the roadmap must be corrected before code is changed.

## Target pipeline

```text
anchor declarations + ordered binders + restrictions + target[point]
→ point-aware CST and AST
→ lexical semantic point environment
→ canonical explicit core
→ point-aware IR1
→ point-aware IR2 and capability requirements
→ one ModelBridge equation per referenced point
→ collision-free backend symbols
→ grouped multi-point evidence
→ real-model replay for every evaluation
```

## Delivery principles

### Documentation first

No implementation patch may introduce syntax or semantics absent from Patch 15-D1. A newly discovered language decision requires a documentation correction before implementation continues.

### One owning layer per patch

Each patch has one primary architectural owner. Necessary adapter changes in adjacent layers are allowed, but a patch must not silently complete work assigned to a later layer.

### Green mainline after every patch

Every patch must pass the complete existing CI suite plus its assigned acceptance cases. Temporary red states across two patches are not allowed.

### Expand, migrate, contract

The chantier follows an expand-and-contract migration:

1. add point-aware structures beside legacy scope structures;
2. route existing one-point behavior through compatibility adapters;
3. add the new syntax and semantics;
4. migrate fixtures and downstream consumers;
5. remove global-output and mutually-exclusive-scope assumptions.

### Representation does not imply execution

Parser or IR acceptance does not imply backend support. Unsupported intermediate capabilities must fail through explicit semantic or backend-capability diagnostics, never through accidental exceptions or unsound lowering.

### No silent legacy reinterpretation

The old forms:

```toetra
at x in neighborhood(...)
```

and:

```toetra
x ~ x'
```

must either retain their historical behavior behind an explicit compatibility path or produce a targeted migration diagnostic. They must never acquire the new semantics silently.

### Stable test identifiers

Every patch description below references the stable IDs defined in the acceptance matrix. Tests should include those IDs in names, parametrization IDs, or comments so that coverage can be audited.

## V1 execution boundary

The completed Patch 15 profile supports:

- global inline anchors;
- one runtime anchor-reference source;
- single and multiple homogeneous quantifier binders;
- ordered nested binder representation;
- direct assertions;
- `where` restrictions;
- natural `neighborhood` membership;
- `check_at` anchor selection sugar;
- `at` universal local sugar;
- one scalar target evaluated at one or more points;
- numeric affine sklearn model equations;
- numeric `Linf` neighborhood lowering;
- universal refutation and existential witness semantics;
- structured rejection of unsupported quantifier alternation;
- grouped multi-point reports and replay.

The completed profile does not promise:

- native execution of alternating quantifiers;
- multiple model outputs;
- multiple anchor-reference sources;
- raw-feature preprocessing reconstruction;
- partial anchors;
- categorical neighborhood encoding;
- nonlinear distance metrics such as executable `L2` constraints;
- several models in one property.

## Patch sequence overview

| Patch | Primary owner | Main outcome | Matrix gate |
|---|---|---|---|
| 15.1 | Grammar and parser | complete target surface syntax reaches CST | P1 |
| 15.2 | AST and builder | all point constructs are represented structurally | P2 |
| 15.3 | Semantic symbols | global anchors and composed point environment | P3 anchors |
| 15.4 | Semantic binding | lexical binders, default-point resolution, indexed targets | P3 binders/defaults/targets |
| 15.5 | Semantic canonicalization | `check_at`, `at`, `where`, and `neighborhood` lower soundly | P4 |
| 15.6 | IR1 | stable point identities, binder chains, restrictions, evaluations | P5 IR1 |
| 15.7 | IR2 | requirements, semantics, assumptions, and alternation gating | P5 IR2 |
| 15.8 | ModelBridge | one deduplicated affine equation per referenced point | P6 ModelBridge |
| 15.9 | Z3 backend | collision-free point symbols and homogeneous multi-point execution | P6 backend |
| 15.10 | Runtime anchors | inline and referenced anchors resolve before execution | P7 runtime resolution |
| 15.11 | Reporting and replay | grouped point evidence and per-point real-model replay | P7 results/replay |
| 15.12 | Consolidation | canonical E2E fixtures, migration, docs, and status closure | P8 |

The order is normative unless a later documentation patch explicitly revises dependencies.

---

## Patch 15.1 — Grammar and parser surface

> Status: Implemented — Gate P1 complete

### Goal

Extend the generated grammar and parser so every accepted source form reaches a faithful CST without changing semantic behavior.

### Required changes

- extend the EBNF first, then regenerate the Lark grammar;
- add global `anchor` declarations after specification constants and before properties;
- add inline anchor blocks and named-argument `ref(...)` bindings;
- add comma-separated quantifier identifiers such as:

```toetra
forall x0, x1
```

- add ordered quantifier-clause chains;
- add `target[identifier]` while retaining unindexed `target`;
- add direct assertion properties without a scope implication;
- add one optional `with domain(...)` after the complete binder chain;
- add one optional `where` restriction after the domain;
- add natural neighborhood membership:

```toetra
where x1 in neighborhood(
    of = x0,
    metric = Linf,
    eps = 0.05
)
```

- add the selected sugar forms:

```toetra
check_at x0 => ...
```

```toetra
at x0 with x1 in neighborhood(
    metric = Linf,
    eps = 0.05
) => ...
```

- preserve indentation as ordinary padding only;
- preserve legacy productions only when needed to issue intentional migration diagnostics later.

### Mandatory acceptance cases

- all `PAR-ANCH-*` cases;
- all `PAR-REF-*` cases;
- all `PAR-QP-*` cases;
- all `PAR-TGT-*` and `PAR-DIR-*` cases;
- all `PAR-WHERE-*`, `PAR-NBH-*`, `PAR-CHK-*`, `PAR-AT-*`, and `PAR-PAIR-*` cases.

### Non-goals

- no AST redesign;
- no point lookup;
- no anchor schema validation;
- no default-point resolution;
- no backend execution.

### Exit criterion

The CST preserves declaration order, binder order, target indices, restriction placement, neighborhood arguments, and source sugar form. Existing grammar-generation and parser regression tests remain green.

---

## Patch 15.2 — AST and builder model

> Status: complete

### Goal

Represent every new source construct as explicit AST data without performing semantic binding.

### Required conceptual structures

- `AnchorDeclarationNode`;
- inline anchor value entries preserving order;
- referenced anchor binding with named arguments;
- an ordered property binder chain;
- quantifier binders with ordered identifier lists or a canonical ordered view;
- optional point identifier on `TargetRefNode`;
- a restriction node separate from the assertion;
- structured neighborhood membership;
- direct property body representation;
- source-specific `check_at` and `at` sugar nodes or equivalent provenance.

The exact class names remain implementation details, but the P2 contract is mandatory.

### Program structure

The AST must expose global anchors separately from scalar specification constants and properties. Anchors must not be smuggled into the header constant table or represented as ordinary assertions.

### Compatibility rule

Legacy one-point AST fixtures may continue to construct compatibility nodes during this patch. Downstream semantic code must not be forced to understand partially built new nodes until Patch 15.3.

### Mandatory acceptance cases

- all `AST-ANCH-*` cases;
- all `AST-QP-*` cases;
- all `AST-TGT-*` cases;
- `AST-WHERE-001`;
- `AST-NBH-001`;
- `AST-CHK-001`;
- `AST-AT-001`;
- `AST-DIR-001`.

### Non-goals

- no semantic symbols;
- no model evaluation identity;
- no sugar lowering;
- no quantifier capability decision.

### Exit criterion

Builder output is deterministic, ordered, source-traceable, and free from semantic point selection. Existing AST golden tests are migrated only where the source shape genuinely changed.

---

## Patch 15.3 — Global anchors and composed point environment

> Status: complete

### Goal

Replace the assumption that a property owns one mutually exclusive scope kind with a composed semantic point environment, beginning with global anchors.

### Required changes

- introduce a first-class semantic point symbol;
- distinguish at least inline anchor, referenced anchor, universal point, and existential point binding kinds;
- register global anchors before property validation;
- preserve declaration provenance and optional concrete/reference payloads;
- validate duplicate anchor names and duplicate inline features;
- validate inline anchors against `ModelSchema` when available;
- enforce transformed-feature-space and complete-anchor V1 policy;
- allow reference lookup metadata that is not a model feature;
- provide a compatibility projection for old consumers that still inspect `SemanticScope`.

### Architecture constraint

`SemanticScope` may remain temporarily as a derived compatibility classification, but it must no longer be the source of truth for point identity or model evaluation selection.

### Mandatory acceptance cases

- `SEM-ANCH-001` through `SEM-ANCH-008`.

### Non-goals

- no runtime row lookup;
- no quantifier-chain execution;
- no `target[x]` model connection;
- no neighborhood lowering.

### Exit criterion

Every global anchor is represented by one immutable semantic point symbol with schema and provenance. Duplicate, incomplete, unknown-feature, and incompatible-type anchors fail at the semantic boundary.

---

## Patch 15.4 — Lexical binders, default points, and indexed targets

> Status: complete

### Goal

Complete semantic point binding for quantified properties and resolve model-output references against explicit point identities.

### Required changes

- process binder clauses in source order;
- expand grouped identifiers left to right into canonical binder frames;
- prohibit duplicate binders, shadowing, and collisions with anchors;
- preserve universal versus existential binding kind;
- validate point-qualified domain subjects and attributes;
- implement the accepted default-point algorithm;
- preserve specification-constant precedence for bare names;
- resolve `target[x0]` into a structured model-output reference;
- resolve short `target` only through one unambiguous default point;
- intern or otherwise deduplicate evaluation identity `(model, point)`;
- reject unknown point indices and no-point/ambiguous short references.

### Mandatory acceptance cases

- `SEM-QP-001` through `SEM-QP-007`;
- `SEM-DEF-001` through `SEM-DEF-010`;
- `SEM-TGT-001` through `SEM-TGT-007`.

### Compatibility rule

Existing single-quantifier specifications retain the short `target` and bare-feature behavior. No multi-point property may inherit positional or innermost-point fallback.

### Non-goals

- no `at` lowering;
- no backend quantifier execution;
- no per-point model equations yet.

### Exit criterion

All accepted feature and target references are bound to exact point symbols. Repeated references to the same point share evaluation identity; different points never do.

---

## Patch 15.5 — Restrictions, neighborhoods, and scope sugar

> Status: complete

### Goal

Lower user-friendly scope syntax into one explicit semantic core before IR1.

### Required changes

- implement `check_at` as declared-anchor default selection without introducing a quantifier;
- implement `at x0 with x1 in neighborhood(...)` as a fresh universal candidate plus neighborhood restriction;
- retain source provenance for generated binders and restrictions;
- represent `where` separately from the asserted property until verification semantics are selected;
- lower universal restrictions as implication at language level;
- lower existential restrictions as conjunction at language level;
- validate neighborhood candidate, anchor, metric, epsilon, and feature-schema compatibility;
- implement the numeric non-negative epsilon rule;
- make `Linf` the initial executable neighborhood profile;
- report unsupported metrics through vocabulary or capability diagnostics;
- introduce explicit migration diagnostics for old `at x in neighborhood(...)` and `x ~ x'` forms if their legacy parser productions are retained.

### Mandatory acceptance cases

- all `LOW-CHK-*` cases;
- all `LOW-AT-*` cases;
- all `LOW-WHERE-*` cases;
- all `LOW-NBH-*` cases.

### Soundness invariant

The following two sources must become canonically equivalent except for provenance:

```toetra
at x0 with x1 in neighborhood(metric = Linf, eps = 0.1)
=> P
```

```toetra
forall x1
where x1 in neighborhood(of = x0, metric = Linf, eps = 0.1)
=> P
```

### Exit criterion

No downstream IR layer needs a separate semantic execution path for `check_at`, `at`, or pairwise scope kinds.

---

## Patch 15.6 — Point-aware IR1

> Status: complete

### Goal

Carry exact point identity, binder order, restrictions, and indexed model-output references through IR1 and NNF normalization.

### Required changes

- introduce or adapt IR1 point-binding artifacts;
- preserve ordered quantifier binders and binding kinds;
- attach domains to exact point identities;
- preserve restrictions separately or lower them only according to the documented quantifier rule;
- replace global target atoms with structured `(model, point, target)` references;
- preserve sugar provenance needed for diagnostics;
- update pretty printers and golden fixtures;
- ensure NNF transforms logical structure without changing point or evaluation identity.

### Mandatory acceptance cases

- `IR1-PNT-001`;
- `IR1-QP-001` and `IR1-QP-002`;
- `IR1-TGT-001`;
- `IR1-RST-001`;
- `IR1-PROV-001`.

### Regression focus

- scalar arithmetic remains recursive and typed;
- open/closed domain boundaries remain unchanged;
- specification constants retain provenance and binding precedence;
- target comparisons with one point remain valid.

### Exit criterion

IR1 can represent every accepted language property without collapsing points into a global entity or flattening alternating binders.

---

## Patch 15.7 — Point-aware IR2 and capability requirements

> Status: complete

### Goal

Build verification tasks that count and preserve model evaluations, select correct universal/existential semantics, and reject unsupported quantifier structures before backend translation.

### Required changes

- extend requirement analysis with point count, anchor count, evaluation count, binder sequence, and alternation depth;
- preserve source-point to IR-point mappings;
- construct universal refutation bodies as restriction AND negated property;
- construct existential witness bodies as restriction AND property;
- retain complete ordered alternating formulas without flattening;
- require native or advanced quantifier capability for alternation;
- reject unsupported alternating chains before solver translation;
- preserve point-owned domain assumptions and anchor facts with provenance;
- deduplicate required model evaluations by `(model, point)`.

### Mandatory acceptance cases

- `IR2-REQ-001` through `IR2-REQ-003`;
- `IR2-SEM-001` and `IR2-SEM-002`;
- `IR2-MAP-001`.

### Non-goals

- no Z3 symbol changes in this patch;
- no runtime row resolution;
- no report schema redesign.

### Exit criterion

Every `VerificationTaskIR2` states exactly which points and model evaluations are required and whether the selected backend profile can soundly execute the quantifier structure.

---

## Patch 15.8 — Per-point ModelBridge equations

> Status: Implemented — Gate P6 ModelBridge complete

### Goal

Generate one backend-neutral model equation for every distinct referenced model evaluation.

### Required changes

- replace single selected input entity logic with evaluation-driven encoding;
- request model constraints from the set of required evaluation identities;
- emit one affine equation per referenced point;
- reuse identical model coefficients and intercept across equations;
- connect concrete anchor feature facts to the matching point symbols;
- emit no model equation for properties that never reference `target`;
- deduplicate repeated references to `target[x0]`;
- update model-output connectivity diagnostics to operate per evaluation.

### Mandatory acceptance cases

- `MB-EVAL-001` through `MB-EVAL-006`.

### Architecture constraint

The model encoder receives explicit evaluation context. It must not inspect a legacy scope and guess which point should feed the model.

### Exit criterion

The model-constraint set contains exactly one sound equation for each requested `(model, point)` pair and none for unrequested points.

---

## Patch 15.9 — Z3 point mapping and multi-point execution

> Status: complete — Gate P6 backend complete

### Goal

Translate point-aware IR2 into collision-free Z3 symbols and execute the supported homogeneous quantifier profile.

### Required changes

- create stable backend names for point-qualified features and outputs;
- ensure `x0.a`, `x1.a`, `target[x0]`, and `target[x1]` remain distinct;
- retain reverse mappings for report construction;
- execute homogeneous universal chains through refutation semantics;
- execute homogeneous existential chains through witness semantics;
- refuse alternating chains before solver calls;
- lower numeric `Linf` neighborhoods into affine constraints over matching features;
- reject unsupported metrics and sorts through capability diagnostics;
- preserve SAT/UNSAT/UNKNOWN interpretation already established for universal and existential tasks.

### Mandatory acceptance cases

- `BE-PNT-001`;
- `BE-TGT-001`;
- `BE-MAP-001`;
- `BE-QP-001` through `BE-QP-003`;
- `BE-NBH-001` and `BE-NBH-002`.

### Initial backend naming policy

The concrete string format is internal, but names must be reversible and collision-free. Semantic identity must not be defined by string concatenation.

### Exit criterion

Two-point numeric affine properties execute without symbol collision, and unsupported alternation or metrics never reach unsound solver translation.

---

## Patch 15.10 — Anchor resolution and runtime API

> Status: complete — Gate P7 runtime resolution complete, including dataset fallback

### Goal

Resolve concrete anchors before compilation/execution while keeping model introspection and point lookup as separate responsibilities.

### Required changes

- introduce an `AnchorResolver` or equivalent runtime abstraction;
- support inline anchors without external lookup;
- support one configured reference source for `ref(key = ..., value = ...)`;
- reject missing, non-unique, missing-key, missing-feature, and dtype-invalid matches;
- project model features in schema order;
- exclude lookup-only metadata from the model vector;
- preserve lookup provenance;
- provide an explicit `verify(...)` anchor input while allowing the compatible introspection dataset to act as the ergonomic default source;
- permit future resolver implementations without adding multi-source DSL syntax now.

### Public API rule

The API keeps the semantic distinction between:

- `dataset`, when used for model/schema introspection;
- the single anchor-reference source used for `ref(...)` lookup.

The same compatible artifact may satisfy both roles. Source selection is custom resolver, then explicit `anchor_source`, then `dataset` fallback. This precedence is part of the public runtime contract.

### Mandatory acceptance cases

- `RUN-REF-001` through `RUN-REF-009`.

### Non-goals

- no multiple named sources;
- no remote lookup protocol;
- no raw preprocessing reconstruction;
- no partial anchor completion.

### Exit criterion

Every anchor entering IR2 is concrete, schema-compatible, immutable, and provenance-bearing. Reference failures occur before backend routing.

---

## Patch 15.11 — Grouped reporting and multi-point replay

### Goal

Expose point-aware evidence without ambiguous flattening and replay every referenced evaluation against the real model.

### Required changes

- replace the report assumption of one flat input vector with grouped point assignments;
- group outputs by evaluation point;
- preserve binding kind and anchor provenance;
- keep convenience flattening only when exactly one point makes it unambiguous;
- version the JSON contract if its shape changes incompatibly;
- update text, HTML, Jupyter, records, and dataframe projections;
- invoke the real model once per distinct referenced point;
- compare each formal output with the corresponding real output;
- reevaluate point relations and the final assertion where supported;
- reject or mark replay incomplete when any required point cannot be reconstructed.

### Mandatory acceptance cases

- `RES-PNT-001` through `RES-PNT-003`;
- `RES-PROV-001` and `RES-PROV-002`;
- `RES-FLAT-001`;
- all `RPL-PNT-*`, `RPL-TGT-*`, `RPL-REL-*`, `RPL-ASSERT-*`, and `RPL-MISS-*` cases.

### Compatibility rule

Existing one-point conveniences such as `input_values` and `output_values` may remain, but they must fail explicitly rather than flattening two points with the same feature names.

### Exit criterion

A user can distinguish every point, every output, every binding origin, and every replay comparison in every public renderer and API view.

---

## Patch 15.12 — End-to-end consolidation and migration closure

### Goal

Close the chantier with canonical fixtures, legacy migration, documentation synchronization, and removal of obsolete assumptions.

### Required changes

- implement all six canonical P8 fixtures;
- compare explicit and sugar artifacts for semantic equivalence;
- migrate existing `check_at`, `at`, pairwise, and target golden fixtures intentionally;
- freeze diagnostics for unsupported alternating quantifiers;
- freeze legacy syntax migration messages;
- remove or isolate obsolete single-global-output code paths;
- remove semantic dependence on mutually exclusive scope kinds;
- update language, compiler, IR, ModelBridge, backend, runtime, and getting-started documentation;
- update the architecture status matrix;
- record final supported and unsupported V1 boundaries;
- run full CI and canonical demonstrations.

### Mandatory acceptance cases

- `E2E-01` through `E2E-06`;
- every regression obligation in the acceptance matrix;
- every completion criterion in the acceptance matrix.

### Exit criterion

Patch 15 was closed when the explicit core and user-facing sugar execute through the same pipeline, multi-point evaluations are sound and replayable, and no old fixture is silently interpreted under a different meaning.

---

## Dependency graph

```text
15.1 Grammar/parser
  ↓
15.2 AST/builder
  ↓
15.3 Anchor environment
  ↓
15.4 Lexical binders + indexed targets
  ↓
15.5 Restrictions + sugar
  ↓
15.6 IR1
  ↓
15.7 IR2 + capabilities
  ↓
15.8 ModelBridge
  ↓
15.9 Z3
  ↓
15.10 Runtime anchor resolution
  ↓
15.11 Reporting + replay
  ↓
15.12 E2E consolidation
```

Patch 15.10 may develop its resolver unit tests in parallel after Patch 15.3, but it must not be integrated before the point-aware IR and execution contracts are stable.

## Cross-patch CI policy

Every patch must run:

```text
ruff
black --check
pyright
pytest
notebook hygiene checks
```

In addition:

- grammar patches regenerate and diff-check `toetra_grammar.lark`;
- AST/IR patches update pretty/golden fixtures intentionally;
- semantic patches add positive and negative complete-program tests;
- backend patches assert capability rejection before solver execution;
- report patches validate JSON schema/version and renderer escaping;
- E2E patches replay on the real sklearn model.

## Review checklist for every patch

A patch is not ready for review unless its description states:

1. which normative invariants it implements;
2. which acceptance IDs it adds;
3. which existing tests or fixtures it migrates;
4. which later capabilities remain intentionally rejected;
5. whether any public artifact shape changes;
6. whether source provenance is preserved;
7. whether the complete CI suite is green.

## Stop-the-line conditions

Implementation must pause for a documentation correction if any patch discovers that:

- point identity cannot be preserved with the accepted representation;
- the parser requires indentation to determine scope;
- one syntax form has two plausible semantic lowerings;
- `target[x]` cannot be distinguished from output selection;
- `where` lowering depends on an unstated quantifier rule;
- a legacy form would be silently reinterpreted;
- report/replay cannot reconstruct the point-to-output mapping;
- a backend would need to flatten alternating quantifiers unsoundly.

## Completion definition

The chantier is complete when:

```text
one or more concrete/symbolic points
→ exact lexical bindings
→ exact point-owned constraints
→ one model evaluation per referenced point
→ sound universal/existential query
→ grouped evidence
→ real-model replay
```

works end to end for the numeric affine V1 profile, while unsupported alternation, metrics, types, and preprocessing boundaries are rejected explicitly.

## Related documents

- ADR-0017 — First-Class Points, Lexical Bindings, and Point-Indexed Model Evaluations
- `language/points-anchors-and-evaluations.md`
- `contracts/point-binding-and-evaluation.md`
- `testing/point-binding-evaluation-test-matrix.md`
- `roadmap/implementation-roadmap.md`

## Closure record

Patch 15.12 delivered the canonical E2E fixtures, stable legacy migration diagnostics, removal of semantic dependence on exclusive scope kinds, final documentation alignment, and a green full-repository `make ci` baseline. Future work must treat the point-aware pipeline as a frozen V1 contract.
