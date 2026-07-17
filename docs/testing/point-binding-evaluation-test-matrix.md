# Point Binding and Evaluation Test Matrix

> Status: Completed normative acceptance matrix — all V1 gates delivered  
> Scope: Anchors, multiple and nested binders, default-point resolution, neighborhoods, indexed targets, per-point model constraints, results, and replay  
> Rule: No implementation patch is complete until its assigned mandatory cases pass

## Purpose

This matrix is the executable specification for the first-class point and indexed-evaluation chantier.

It defines:

- stable test identifiers;
- owning compiler or runtime layer;
- accepted and rejected source forms;
- mandatory artifact invariants;
- cross-layer semantic equivalences;
- end-to-end evidence requirements.

This document does not redefine patch sequencing. The accepted mapping from gates and case IDs to implementation patches is maintained in `roadmap/point-binding-evaluation-implementation-roadmap.md`.

## Complete-program rule

Parser, builder-from-source, semantic-from-source, pipeline, and end-to-end cases MUST use complete `.forml` programs with required `model` and `target` declarations.

Short fragments shown in tables are case labels only, except for pure lexer or helper tests.

## Gate P0 — Documentation and contract freeze

| ID | Obligation | Expected |
|---|---|---|
| DOC-PNT-001 | ADR-0017 accepted | point/binding/evaluation separation is authoritative |
| DOC-PNT-002 | language specification published | canonical syntax and invalid forms are frozen |
| DOC-PNT-003 | cross-layer contract published | preservation invariants are frozen |
| DOC-PNT-004 | acceptance matrix published | implementation patches reference stable case IDs |
| DOC-PNT-005 | legacy conflicts identified | provisional scope behavior is marked for migration |

### P0 invariant

No code modification is part of P0. Later implementation changes must not invent semantics absent from the accepted documents.

## Gate P1 — Grammar and parser

> Implementation status: complete in Patch 15.1
> Frozen parser choices: inline-anchor trailing commas are accepted; duplicate anchor/ref/binder names remain parseable for later semantic rejection; positional `ref(...)` and deferred `source = ...` are rejected; legacy `at` and `x ~ x'` remain distinguishable CST branches.

### Anchor declarations

| ID | Case label | Expected |
|---|---|---|
| PAR-ANCH-001 | `anchor x0 := { age: 42 }` | complete program parses |
| PAR-ANCH-002 | multiple inline features | order and literals preserved |
| PAR-ANCH-003 | trailing comma in anchor block | accepted if chosen grammar style is consistent |
| PAR-ANCH-004 | empty anchor block | parser rejection in initial profile |
| PAR-ANCH-005 | missing anchor identifier | parser rejection |
| PAR-ANCH-006 | `x0.age = 42` inside anchor block | parser rejection |
| PAR-ANCH-007 | missing `:` between feature and value | parser rejection |
| PAR-ANCH-008 | duplicate feature spelling | parse may succeed; semantic rejection owned later |
| PAR-ANCH-009 | anchor after first property | parser rejection if declarations are header-body ordered |

### Referenced anchors

| ID | Case label | Expected |
|---|---|---|
| PAR-REF-001 | `anchor x0 := ref(key = "id", value = "42")` | parse |
| PAR-REF-002 | multiline `ref(...)` | parse |
| PAR-REF-003 | missing key argument | parse if generic named arguments are preserved; semantic rejection later |
| PAR-REF-004 | duplicate key argument | parse or parser rejection according to named-argument grammar; behavior frozen by test |
| PAR-REF-005 | positional `ref("id", "42")` | parser rejection in initial profile |
| PAR-REF-006 | `source = "validation"` in initial profile | parser or semantic rejection with explicit deferred-feature diagnostic; never ignored |

### Quantifier lists and chains

| ID | Case label | Expected |
|---|---|---|
| PAR-QP-001 | `forall x0, x1` | parse ordered identifier list |
| PAR-QP-002 | `exists x0, x1` | parse ordered identifier list |
| PAR-QP-003 | `forall x0` then `exists x1` | parse ordered binder chain |
| PAR-QP-004 | indented nested clauses | same CST semantics as unindented form |
| PAR-QP-005 | trailing comma in binder list | parser rejection unless explicitly accepted later |
| PAR-QP-006 | duplicate name in one binder list | parse; semantic rejection later |
| PAR-QP-007 | missing identifier after comma | parser rejection |
| PAR-QP-008 | domain after full binder chain | parse |
| PAR-QP-009 | `where` after domain | parse |
| PAR-QP-010 | `where` before domain | parser rejection in canonical grammar |

### Indexed target and direct assertions

| ID | Case label | Expected |
|---|---|---|
| PAR-TGT-001 | `target[x0] <= 7` | parse target index structurally |
| PAR-TGT-002 | `target <= 7` | preserve unindexed target |
| PAR-TGT-003 | `target[]` | parser rejection |
| PAR-TGT-004 | `target[x0, x1]` | parser rejection |
| PAR-TGT-005 | `target["x0"]` | parser rejection |
| PAR-DIR-001 | property contains direct assertion without `=>` | parse |
| PAR-DIR-002 | scoped property retains `=>` | parse |

### Restrictions and sugar

| ID | Case label | Expected |
|---|---|---|
| PAR-WHERE-001 | `where x1.age >= x0.age` | parse restriction expression |
| PAR-WHERE-002 | parenthesized compound restriction | parse logical structure |
| PAR-NBH-001 | `where x1 in neighborhood(of = x0, metric = Linf, eps = 0.05)` | parse structured membership |
| PAR-NBH-002 | missing candidate before `in` | parser rejection |
| PAR-NBH-003 | missing `of` | parser or semantic rejection according to named-argument grammar |
| PAR-NBH-004 | missing metric | parser or semantic rejection according to named-argument grammar |
| PAR-NBH-005 | missing eps | parser or semantic rejection according to named-argument grammar |
| PAR-CHK-001 | `check_at x0 => ...` | parse selection sugar |
| PAR-AT-001 | `at x0 with x1 in neighborhood(metric = Linf, eps = 0.05)` | parse local sugar |
| PAR-AT-002 | old `at x in neighborhood(...)` | migration rejection or explicit legacy parse, never silent new meaning |
| PAR-PAIR-001 | old `x ~ x'` | migration rejection or explicit legacy parse, never target-core interpretation |

### P1 invariant

The CST preserves anchor declaration order, point spelling, binder-list order, binder-clause order, target indices, restriction placement, neighborhood arguments, and sugar provenance.

## Gate P2 — AST and builder

| ID | Case label | Required AST invariant |
|---|---|---|
| AST-ANCH-001 | inline anchor | structured declaration with ordered feature/value entries |
| AST-ANCH-002 | referenced anchor | structured `ref` binding with named arguments |
| AST-QP-001 | `forall x0, x1` | grouped source identifiers preserved or canonical binders available in source order |
| AST-QP-002 | `forall x0` / `exists x1` | two ordered binder nodes, not a dictionary |
| AST-TGT-001 | `target[x0]` | target node stores optional point identifier |
| AST-TGT-002 | unindexed `target` | target node stores no point identifier |
| AST-WHERE-001 | generic restriction | boolean expression preserved separately from assertion |
| AST-NBH-001 | neighborhood membership | candidate, anchor, metric, epsilon structured |
| AST-CHK-001 | `check_at` | selected anchor and source span preserved |
| AST-AT-001 | `at` | anchor, candidate, neighborhood arguments and source span preserved |
| AST-DIR-001 | direct property | property body distinguishes direct assertion from scoped form |

### P2 invariant

No AST builder performs semantic point lookup, default-point choice, model evaluation creation, or quantifier capability decisions.

## Gate P3 — Semantic point environment

### Anchor registration

| ID | Case label | Expected |
|---|---|---|
| SEM-ANCH-001 | unique inline anchor | register concrete immutable point symbol |
| SEM-ANCH-002 | unique referenced anchor | register unresolved concrete point binding |
| SEM-ANCH-003 | duplicate anchor identifier | structured rejection |
| SEM-ANCH-004 | duplicate feature in anchor | structured rejection |
| SEM-ANCH-005 | unknown model feature | structured rejection after schema availability |
| SEM-ANCH-006 | missing model feature | structured incomplete-anchor rejection in V1 profile |
| SEM-ANCH-007 | incompatible literal dtype | structured type rejection |
| SEM-ANCH-008 | lookup key not a model feature | accepted as reference metadata |

### Binder registration and lexical order

| ID | Case label | Expected |
|---|---|---|
| SEM-QP-001 | `forall x0, x1` | two universal point symbols in left-to-right frames |
| SEM-QP-002 | `forall x0` then `exists x1` | preserve universal/existential order |
| SEM-QP-003 | duplicate name in binder list | rejection |
| SEM-QP-004 | shadow outer binder | rejection |
| SEM-QP-005 | collide with global anchor | rejection |
| SEM-QP-006 | reference outer point from inner restriction | accepted |
| SEM-QP-007 | reference unknown point | rejection |

### Default-point resolution

| ID | Case label | Expected |
|---|---|---|
| SEM-DEF-001 | one quantified point + bare feature | resolve to that point |
| SEM-DEF-002 | one quantified point + unindexed target | resolve to that point evaluation |
| SEM-DEF-003 | one global anchor + direct bare target | resolve to anchor |
| SEM-DEF-004 | two global anchors + bare target | ambiguity rejection |
| SEM-DEF-005 | two quantified points + bare feature | ambiguity rejection |
| SEM-DEF-006 | two quantified points + bare target | ambiguity rejection |
| SEM-DEF-007 | `check_at candidate` among two anchors | select candidate as default |
| SEM-DEF-008 | no point + bare target | no-point rejection |
| SEM-DEF-009 | specification constant collides with feature shorthand | constant keeps existing lookup precedence |
| SEM-DEF-010 | explicit `x0.feature` | always resolves to point feature |

### Indexed targets

| ID | Case label | Expected |
|---|---|---|
| SEM-TGT-001 | `target[x0]` with visible point | structured model-output reference |
| SEM-TGT-002 | `target[x1]` with unknown point | rejection |
| SEM-TGT-003 | target indexed by anchor | accepted |
| SEM-TGT-004 | target indexed by universal point | accepted |
| SEM-TGT-005 | target indexed by existential point | accepted |
| SEM-TGT-006 | repeated `target[x0]` | same semantic evaluation identity |
| SEM-TGT-007 | `target[x0]` and `target[x1]` | distinct semantic evaluation identities |

### P3 invariant

Every accepted point and output reference is exact, typed when schema data exists, and traceable to its source binding. No single-variable alias fallback exists for unknown explicit points.

## Gate P4 — Sugar and restriction semantics

> Status: complete

### `check_at`

| ID | Case label | Expected canonical semantics |
|---|---|---|
| LOW-CHK-001 | declared anchor selected | default point set to anchor, no quantifier |
| LOW-CHK-002 | undeclared point selected | rejection before IR1 |
| LOW-CHK-003 | symbolic point selected | rejection: `check_at` requires concrete anchor |
| LOW-CHK-004 | implicit target in assertion | resolved to selected anchor |

### `at`

| ID | Case label | Expected canonical semantics |
|---|---|---|
| LOW-AT-001 | valid local form | fresh universal candidate + neighborhood restriction |
| LOW-AT-002 | undeclared anchor | rejection |
| LOW-AT-003 | candidate name collides | rejection |
| LOW-AT-004 | source span | generated binder/restriction retains sugar provenance |
| LOW-AT-005 | explicit indexed outputs | both anchor and candidate evaluations preserved |

### `where`

| ID | Case label | Expected canonical semantics |
|---|---|---|
| LOW-WHERE-001 | universal + restriction | implication at language level |
| LOW-WHERE-002 | existential + restriction | conjunction at language level |
| LOW-WHERE-003 | universal refutation | query contains restriction AND negated property |
| LOW-WHERE-004 | existential witness | query contains restriction AND property |
| LOW-WHERE-005 | compound restriction | boolean structure preserved |

### Neighborhood

| ID | Case label | Expected |
|---|---|---|
| LOW-NBH-001 | valid Linf neighborhood | relation lowered over matching point features |
| LOW-NBH-002 | negative epsilon | semantic rejection |
| LOW-NBH-003 | non-numeric epsilon | type rejection |
| LOW-NBH-004 | unknown metric | vocabulary or capability rejection |
| LOW-NBH-005 | candidate equals anchor identifier | rejection in initial profile |
| LOW-NBH-006 | feature schema mismatch | structured lowering failure |

### P4 invariant

Sugar produces the same canonical semantics as the explicit source form. Universal and existential restrictions never share the wrong connective.

## Gate P5 — IR1 and IR2 preservation

| ID | Case label | Required invariant |
|---|---|---|
| IR1-PNT-001 | two point bindings | distinct stable point identities |
| IR1-QP-001 | homogeneous binder chain | order and quantifier kinds preserved |
| IR1-QP-002 | alternating binder chain | order preserved without flattening |
| IR1-TGT-001 | indexed output | structured model/point/target reference |
| IR1-RST-001 | restriction | preserved separately or lowered with documented quantifier semantics |
| IR1-PROV-001 | `at` sugar | source provenance retained |
| IR2-REQ-001 | two referenced outputs | requirement reports two model evaluations |
| IR2-REQ-002 | point-only property | zero model evaluations required |
| IR2-REQ-003 | alternating quantifiers | native/advanced quantifier capability required |
| IR2-SEM-001 | universal pairwise property | refutation semantics retained |
| IR2-SEM-002 | existential pair search | satisfaction semantics retained |
| IR2-MAP-001 | identity map | source point → IR point → backend symbols mapping available |

### P5 invariant

No normalization step merges point identities, loses binder ordering, or replaces structured evaluation references with an untraceable global target.

## Gate P6 — ModelBridge and backend

### ModelBridge

| ID | Case label | Expected |
|---|---|---|
| MB-EVAL-001 | only `target[x0]` referenced | one affine equation for x0 |
| MB-EVAL-002 | repeated `target[x0]` | one deduplicated affine equation |
| MB-EVAL-003 | `target[x0]` and `target[x1]` | two affine equations |
| MB-EVAL-004 | shared model | coefficients/intercept identical across equations |
| MB-EVAL-005 | point-only assertion | no unnecessary model equation |
| MB-EVAL-006 | concrete anchor | anchor values connected to x0 feature symbols |

### Backend naming and translation

| ID | Case label | Expected |
|---|---|---|
| BE-PNT-001 | same feature on x0/x1 | distinct solver symbols |
| BE-TGT-001 | target x0/x1 | distinct solver output symbols |
| BE-MAP-001 | solver model returned | reverse mapping restores point/evaluation identities |
| BE-QP-001 | homogeneous universal chain | executable through refutation profile |
| BE-QP-002 | homogeneous existential chain | executable through witness profile |
| BE-QP-003 | alternating chain unsupported | structured capability rejection before solver execution |
| BE-NBH-001 | supported Linf lowering | backend query receives complete constraints |
| BE-NBH-002 | unsupported metric | structured capability rejection |

### P6 invariant

Distinct points never collide in solver symbols, and every requested model evaluation is connected exactly once.

## Gate P7 — Anchor resolution, results, and replay

### Referenced anchor resolution

| ID | Case label | Expected |
|---|---|---|
| RUN-REF-001 | one matching row | resolved concrete point |
| RUN-REF-002 | no matching row | structured failure before backend |
| RUN-REF-003 | multiple matching rows | structured non-unique failure |
| RUN-REF-004 | missing key column | structured failure |
| RUN-REF-005 | missing model feature | structured failure |
| RUN-REF-006 | lookup metadata not model feature | accepted and excluded from model vector |
| RUN-REF-007 | dtype mismatch | structured failure |
| RUN-REF-008 | dataset supplied, no explicit anchor source | dataset reused as default lookup source |
| RUN-REF-009 | dataset and explicit anchor source supplied | explicit anchor source wins |
| RUN-REF-010 | reused dataset contains lookup-only string metadata | metadata excluded from model schema and backend scalar sorts |

### Result shape

| ID | Case label | Expected |
|---|---|---|
| RES-PNT-001 | one-point counterexample | evidence grouped under x0 |
| RES-PNT-002 | two-point counterexample | distinct x0/x1 values and outputs |
| RES-PNT-003 | existential two-point witness | result kind is witness, not counterexample |
| RES-PROV-001 | inline anchor | declaration provenance retained |
| RES-PROV-002 | referenced anchor | lookup provenance retained without confusing key metadata with features |
| RES-FLAT-001 | same feature names on two points | public API does not flatten ambiguously |

### Replay

| ID | Case label | Expected |
|---|---|---|
| RPL-PNT-001 | one evaluation | real model invoked once |
| RPL-PNT-002 | two evaluations | real model invoked for both distinct points |
| RPL-PNT-003 | repeated same evaluation reference | no semantic duplication |
| RPL-TGT-001 | formal/concrete output comparison | performed per point |
| RPL-REL-001 | pair relation | reevaluated from concrete point values |
| RPL-ASSERT-001 | final assertion | reevaluated using concrete outputs |
| RPL-MISS-001 | one point cannot be reconstructed | replay marked incomplete/failure, never silently partial |

### P7 invariant

The public result and replay preserve all point identities and all referenced model evaluations.

## Gate P8 — Canonical end-to-end fixtures

### E2E-01 — Inline anchor direct check

```forml
model := "linear.joblib"
target := score

anchor x0 := {
    a: 1.0,
    b: 2.0
}

[BOUND]:
target[x0] <= 7 using Z3
```

Required assertions:

- anchor parses and binds;
- one evaluation is generated;
- output is connected to x0;
- result exposes x0 and `target[x0]`;
- replay matches the real model.

### E2E-02 — Referenced anchor with `check_at`

```forml
model := "linear.joblib"
target := score

anchor row := ref(
    key = "id",
    value = "R-42"
)

[BOUND]:
check_at row
=> target <= 7 using Z3
```

Required assertions:

- one row is resolved from the runtime source;
- `target` resolves to `target[row]`;
- lookup metadata is not encoded as a feature;
- result retains anchor-reference provenance.

### E2E-03 — Two-point universal property

```forml
model := "linear.joblib"
target := score

[MONOTONICITY]:
forall x0, x1
with domain(
    x0.a: [0, 3],
    x1.a: [0, 3]
)
where x1.a >= x0.a
=> target[x1] >= target[x0] using Z3
```

Required assertions:

- two point symbols and two evaluations;
- universal refutation query contains relation and negated property;
- SAT yields a two-point counterexample;
- UNSAT yields proof;
- evidence remains grouped by point.

### E2E-04 — Local robustness sugar equivalence

Sugar fixture:

```forml
anchor x0 := { a: 1.0 }

[ROBUSTNESS]:
at x0 with x1 in neighborhood(
    metric = Linf,
    eps = 0.1
)
=> (target[x1] - target[x0] <= 0.2)
   and (target[x0] - target[x1] <= 0.2) using Z3
```

Explicit fixture:

```forml
anchor x0 := { a: 1.0 }

[ROBUSTNESS]:
forall x1
where x1 in neighborhood(
    of = x0,
    metric = Linf,
    eps = 0.1
)
=> (target[x1] - target[x0] <= 0.2)
   and (target[x0] - target[x1] <= 0.2) using Z3
```

Required assertion:

- both forms produce semantically equivalent canonical artifacts and the same verification result, excluding source-provenance differences.

### E2E-05 — Existential adversarial witness

```forml
anchor x0 := { a: 1.0 }

[ROBUSTNESS]:
exists x1
where x1 in neighborhood(
    of = x0,
    metric = Linf,
    eps = 0.1
)
=> (target[x1] - target[x0] > 0.2)
   or (target[x0] - target[x1] > 0.2) using Z3
```

Required assertions:

- SAT is interpreted as witness;
- x0 and x1 are both exposed;
- both model evaluations are replayed;
- no universal counterexample terminology is used.

### E2E-06 — Alternating quantifier capability rejection

```forml
[LOGIC]:
forall x0
exists x1
with domain(
    x0.a: [0, 3],
    x1.a: [0, 3]
)
=> target[x1] >= target[x0] using Z3
```

Required assertions:

- source parses;
- AST and semantic artifacts preserve order;
- IR requirements record alternation;
- unsupported initial backend profile rejects before solver translation;
- no flat free-variable query is produced.

## Regression obligations

Throughout the chantier:

- existing specification constants remain valid;
- typed domains retain open/closed boundaries;
- scalar arithmetic and target comparisons remain valid;
- current affine Z3 proof/counterexample behavior remains green for migrated fixtures;
- public result serialization remains versioned;
- legacy provisional scope fixtures are either migrated or receive intentional migration diagnostics;
- no patch may silently reinterpret an old fixture under new semantics.

## Completion criteria

The chantier is complete only when:

1. all mandatory P1–P7 cases assigned to the V1 profile pass;
2. canonical P8 fixtures pass end to end;
3. alternating quantifier cases are either supported or rejected soundly by capability;
4. no global unindexed model output remains in multi-point internal artifacts;
5. reports and replay preserve every point and evaluation;
6. documentation examples match implemented syntax;
7. old scope semantics are removed or explicitly migrated.

## Related documents

- ADR-0017 — First-Class Points, Lexical Bindings, and Point-Indexed Model Evaluations
- `language/points-anchors-and-evaluations.md`
- `contracts/point-binding-and-evaluation.md`
- `roadmap/point-binding-evaluation-implementation-roadmap.md`

## Completion record

All mandatory V1 gates and E2E-01 through E2E-06 are implemented. Alternating quantifiers satisfy the matrix through sound capability rejection. This matrix remains the regression contract for future changes.
