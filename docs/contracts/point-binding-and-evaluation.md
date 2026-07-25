# Point Binding and Model Evaluation Contract

> Status: Accepted target contract — implemented through point-aware IR2  
> Scope: Source, CST, AST, semantic environment, IR1, IR2, ModelBridge, backend, runtime, replay  
> Priority: P0  
> Audience: compiler contributors, backend authors, runtime authors, test and mutation authors

## Purpose

This contract defines the information that every Toetra layer must preserve when a specification introduces concrete or symbolic points and evaluates the same model at one or more of those points.

The contracted pipeline is:

```text
source point declarations and binders
→ CST tokens and ordering
→ typed AST nodes
→ lexical semantic point environment
→ point-aware IR1
→ point-aware IR2 and verification semantics
→ per-point ModelBridge assumptions
→ backend symbols and solver query
→ grouped point evidence
→ real-model multi-point replay
```

The contract prevents any layer from silently collapsing distinct points or distinct model evaluations into one global entity.

## Normative invariants

The following invariants apply across all layers.

### INV-PNT-001 — Exact point identity

A source point identifier MUST remain traceable through semantic symbols, IR, diagnostics, backend names, results, and replay.

### INV-PNT-002 — Single binding

Every point is introduced by exactly one binding. Unknown, duplicate, or shadowed point identifiers MUST be rejected by the owning semantic boundary.

### INV-PNT-003 — Ordered binders

Quantifier order MUST be preserved. Binder chains MUST NOT be stored as unordered mappings or sets.

### INV-PNT-004 — Binding kind preservation

The system MUST distinguish concrete anchors, universal symbolic points, and existential symbolic points.

### INV-PNT-005 — No implicit point invention

Except for deterministic sugar desugaring, a compiler layer MUST NOT invent an unnamed or primed point.

### INV-EVAL-001 — Evaluation identity

A model evaluation is identified by `(model identity, point identity)`.

### INV-EVAL-002 — Distinct points, distinct outputs

`target[x0]` and `target[x1]` MUST map to distinct output symbols when `x0 != x1`.

### INV-EVAL-003 — Repeated reference reuse

Repeated `target[x0]` references MUST reuse one evaluation identity and one model equation.

### INV-EVAL-004 — Single target definition

The V1 model header defines one scalar target. Point indexing selects the input point, not a target from an output list.

### INV-RES-001 — Unique implicit point

A short target or feature reference may resolve implicitly only when exactly one eligible default point exists.

### INV-RES-002 — No fallback under ambiguity

The compiler MUST NOT choose the first, last, or innermost point silently when resolution is ambiguous.

### INV-RST-001 — Quantifier-sensitive restriction lowering

`where R => P` lowers to implication for universal binders and conjunction for existential binders.

### INV-SUG-001 — Sugar semantic equivalence

`check_at` and `at` MUST lower to the explicit core without introducing a separate backend path.

### INV-RUN-001 — Complete multi-point evidence

A result involving several points MUST preserve each point's values, binding provenance, and referenced output.

### INV-RPL-001 — Replay all evaluations

Replay MUST invoke the real model once per distinct referenced point and compare every formal output with the corresponding concrete output.

## Source-to-CST contract

### Inputs

The source may contain:

- inline anchor declarations;
- referenced anchor declarations;
- binder lists;
- ordered binder chains;
- indexed target references;
- direct assertion properties;
- `where` restrictions;
- natural neighborhood membership;
- `check_at` and `at` sugar.

### Preservation requirements

The CST MUST preserve:

- anchor declaration order;
- anchor identifier spelling;
- inline feature order and literal tokens;
- `ref` argument names, order, and values;
- every quantifier token and its identifier list;
- binder clause order;
- indentation as trivia only, if retained at all;
- target index identifier;
- `where` placement;
- neighborhood candidate, anchor, metric, and epsilon tokens;
- source form provenance for `check_at` and `at`.

### Syntax ownership

The parser owns rejection of:

- missing anchor identifiers;
- malformed anchor blocks;
- malformed `ref(...)` argument syntax;
- empty binder lists;
- missing target index closing bracket;
- malformed neighborhood membership;
- incomplete `at ... with ... in neighborhood(...)` syntax;
- structurally invalid property forms.

The parser does not own model feature validation, point visibility, ambiguity, type compatibility, or backend capability.

## CST-to-AST contract

### Required conceptual AST artifacts

Implementation names may differ, but the AST MUST represent the following concepts structurally:

```text
AnchorDeclaration
├── name
├── binding
│   ├── InlinePointValue
│   │   └── ordered feature/value entries
│   └── AnchorReference
│       └── named arguments
└── source span
```

```text
QuantifierChain
└── ordered QuantifierBinder[]
    ├── quantifier kind
    ├── ordered point identifiers
    └── source span
```

Binder lists MAY remain grouped in raw AST for source fidelity, but a canonical desugared view MUST be available and left-to-right ordered.

```text
TargetReference
├── optional point identifier
└── source span
```

```text
NeighborhoodRestriction
├── candidate point
├── anchor point
├── metric
├── epsilon expression
└── source span
```

```text
PropertyBody
├── direct assertion
└── or scoped form
    ├── explicit quantifier chain
    ├── check-at sugar
    └── at sugar
```

### AST invariants

- Point identifiers remain strings or dedicated identifier values, not pre-bound semantic objects.
- Target point indices are not converted to model output names in AST.
- Quantifier order is never flattened into a dictionary.
- Inline anchor entries remain structured and ordered.
- `at` and `check_at` source provenance is retained at least until semantic desugaring diagnostics can reference it.

## AST-to-semantic contract

### Semantic environment

The semantic layer MUST construct a composed environment with at least:

```text
PointEnvironment
├── global anchor symbols
├── lexical quantifier frames
├── selected default point, if unique or explicitly selected
├── point-owned domains
├── restrictions and relations
└── required model evaluations
```

### Point symbol

Each point symbol MUST expose conceptually:

```text
PointSymbol
├── name
├── binding kind
├── feature schema
├── declaration provenance
├── lexical depth
├── optional concrete value
└── optional reference provenance
```

### Registration order

1. Register global anchor declarations.
2. Validate anchor name uniqueness.
3. Enter a property environment containing visible anchors.
4. Process quantifier binders left to right.
5. Create one lexical frame per canonical binder.
6. Validate domain subjects and restrictions against visible point symbols.
7. Resolve assertion references.
8. Collect required model evaluations.

### Semantic rejections

The semantic layer owns:

- duplicate anchor names;
- binder name collisions with visible anchors;
- quantifier shadowing;
- unknown explicit point references;
- unknown target indices;
- `check_at` selecting a non-anchor;
- `at` selecting a non-anchor;
- `at` candidate collisions;
- anchor feature mismatch with model schema;
- reference key/value type policy violations when schema is available;
- ambiguous implicit feature or target references;
- neighborhood references to unknown points;
- negative or non-numeric epsilon after scalar typing;
- incompatible domain ownership.

### Default-point resolution

The semantic layer MUST distinguish:

- points visible in the lexical environment;
- points eligible as implicit model-input defaults;
- points explicitly selected by `check_at`;
- points referenced by an indexed target.

Resolution algorithm:

```text
explicit check_at selection present → selected anchor
else exactly one eligible point      → that point
else zero eligible points            → no-point diagnostic
else                                  → ambiguity diagnostic
```

No positional fallback is allowed.

### Target resolution

```toetra
target[x0]
```

resolves to a semantic model-output reference containing:

```text
model identity
point symbol x0
target name from header
target dtype from model schema when available
source provenance
```

A short `target` first resolves the default point, then produces the same structured reference.

## Sugar lowering contract

Sugar lowering SHOULD occur after binding validation has enough information to report user-facing source errors, but before IR1 relies on semantic scope categories.

### `check_at`

Source:

```toetra
check_at x0
=> P
```

Preconditions:

- `x0` is a declared anchor.

Canonical semantic form:

```text
default point = x0
assertion = P with implicit references resolved through x0
```

No quantifier is introduced.

### `at`

Source:

```toetra
at x0 with x1 in neighborhood(metric = M, eps = E)
=> P
```

Preconditions:

- `x0` is a declared anchor;
- `x1` is fresh;
- `M` and `E` are valid neighborhood arguments.

Canonical semantic form:

```toetra
forall x1
where x1 in neighborhood(of = x0, metric = M, eps = E)
=> P
```

The canonical form MUST retain provenance linking the generated binder and restriction to the `at` source span.

## Restriction lowering contract

A restriction remains distinct from the asserted property until verification semantics are selected.

For a universal source binder:

```text
source property: forall x where R => P
language formula: forall x. R -> P
refutation query body: R and not P
```

For an existential source binder:

```text
source property: exists x where R => P
language formula: exists x. R and P
witness query body: R and P
```

This distinction MUST be tested independently from backend quantifier support.

For multiple homogeneous binders, the same polarity applies to the complete chain.

For an alternating chain, the single `where` clause is attached to the innermost binder and may reference every point visible in that lexical position. Its implication-or-conjunction interpretation follows that innermost quantifier. The complete ordered quantifier structure remains part of the formula.

The IR MUST preserve that structure and defer to capability-aware execution. It MUST NOT produce a flat conjunction over free variables.

## Semantic-to-IR1 contract

IR1 MUST preserve:

- point symbols and binding kinds;
- canonical binder order;
- quantifier source intent;
- point-owned domain constraints;
- restrictions distinct from the property assertion until documented lowering;
- point-indexed target references;
- sugar provenance when needed for diagnostics;
- source spans or stable provenance identifiers.

Recommended conceptual structures:

```text
PointBindingIR
QuantifierBinderIR
PointDomainIR
RestrictionIR
ModelOutputRefIR(model, point, target)
```

Exact class names are implementation decisions. The invariants are normative.

IR1 normalization MUST NOT rename two source points to the same identity.

## IR1-to-IR2 contract

IR2 requirement analysis MUST determine at least:

- number of symbolic points;
- number of concrete anchors;
- number of distinct model evaluations;
- presence of neighborhood expansion;
- quantifier chain and alternation depth;
- universal refutation or existential satisfaction semantics;
- backend requirement for native or finite-expanded quantifiers;
- arithmetic requirements introduced by neighborhood lowering.

IR2 MUST retain a mapping:

```text
source point
→ IR point identity
→ backend point symbols
```

and:

```text
(model, point)
→ model evaluation identity
→ target symbol
```

## ModelBridge contract

### Input selection

ModelBridge MUST receive explicit requested evaluation identities. It MUST NOT select one arbitrary scope entity.

### Per-point affine constraints

For each distinct referenced point `p`, an affine model contributes exactly one constraint:

```text
target[p] = intercept + Σ coefficient_i * p.feature_i
```

### Deduplication

If `target[p]` occurs several times, ModelBridge contributes one equation for `p`.

### Multiple points

If both `target[x0]` and `target[x1]` are referenced, ModelBridge contributes two equations with shared model parameters and distinct point variables.

### Concrete anchors

Concrete anchor feature values may be emitted as assumptions or substituted according to the chosen IR policy. Their provenance MUST remain recoverable.

### No-output properties

A property that never references the model output MUST NOT force an unnecessary model evaluation solely because points are present.

## IR2-to-backend contract

### Backend naming

A backend may flatten structured identities into solver symbol names, for example:

```text
x0__age
_model__x0__RiskScore
```

The backend MUST preserve a reverse mapping to structured identities. The flattened string is not the semantic source of truth.

### Capability checks

Before translation, the backend route MUST reject unsupported requirements such as:

- quantifier alternation;
- unsupported neighborhood metric;
- unsupported scalar operations introduced by neighborhood expansion;
- unsupported point value types;
- unsupported output arity.

### Result interpretation

For universal source semantics:

```text
UNSAT(refutation query) → proof
SAT(refutation query)   → counterexample
```

For existential source semantics:

```text
SAT(witness query)   → witness
UNSAT(witness query) → no witness
```

Point count does not change this rule. Source quantification does.

## Runtime anchor-resolution contract

The runtime MAY support inline, referenced, and API-provided concrete bindings through one normalized point-value representation.

For the initial single-source profile, source selection MUST follow this order:

1. a caller-provided custom resolver;
2. a caller-provided dedicated anchor source;
3. a compatible dataset artifact already supplied for model/schema introspection;
4. otherwise, a structured source-required failure.

This fallback MUST NOT transfer row-lookup responsibility to model introspection. It only allows the same physical artifact to satisfy two distinct runtime roles. Explicit anchor inputs MUST take precedence over the dataset fallback.

A referenced-anchor resolver MUST return either:

```text
ResolvedPoint(name, feature_values, provenance)
```

or a structured failure.

Required failure classes include:

- source missing;
- key column missing;
- no matching point;
- multiple matching points;
- model feature missing;
- unexpected feature policy violation;
- type mismatch;
- preprocessing-space mismatch when detectable.

The resolver MUST run before backend execution and MUST NOT encode missing values as unconstrained symbolic features silently.

When a dataset serves both introspection and anchor lookup, the model input contract remains authoritative. Lookup-only or provenance columns MUST be excluded from `ModelSchema.features` and from resolved point vectors. For sklearn models, `feature_names_in_` determines the ordered model inputs when present; dataset-only inference is a fallback for estimators without named-input metadata.

## Result and trace contract

A result MUST support grouped evidence by point.

Conceptual shape:

```text
VerificationEvidence
├── points: map[PointId, PointEvidence]
│   └── PointEvidence
│       ├── binding kind
│       ├── source values
│       ├── solver values
│       ├── provenance
│       └── outputs: map[EvaluationId, OutputEvidence]
├── relations
├── assertion evaluation
└── diagnostics
```

The public API MAY expose convenience projections, but it MUST NOT flatten same-named features from several points into one ambiguous map.

## Replay contract

Replay steps:

1. identify every distinct model evaluation referenced by the verification task;
2. reconstruct the corresponding point in model feature order;
3. run the real model for each point;
4. normalize every concrete output;
5. compare it with the formal target for that point;
6. reevaluate point relations and the final assertion;
7. report mismatches with point and evaluation identities.

A multi-point replay succeeds only when all referenced evaluations and the final property interpretation are consistent.

## Diagnostic contract

Minimum target diagnostic families:

| Code family | Meaning |
|---|---|
| `POINT_*` | declaration, visibility, shadowing, ambiguity |
| `ANCHOR_*` | inline or referenced concrete binding failures |
| `TARGET_POINT_*` | invalid or ambiguous target indexing |
| `QUANTIFIER_*` | binder structure or unsupported alternation |
| `NEIGHBORHOOD_*` | relation arguments or capability mismatch |
| `MODEL_EVALUATION_*` | missing, duplicate, or disconnected evaluation |
| `REPLAY_POINT_*` | concrete multi-point replay mismatch |

Exact final codes are a roadmap decision, but failures MUST remain structured and layer-owned.

## Mutation and property-based testing hooks

Miova or property-based campaigns SHOULD challenge:

- point identifier replacement;
- binder reordering;
- binder duplication;
- shadowing introduction;
- target index deletion;
- target index substitution;
- anchor feature deletion or duplication;
- `ref` key/value mutation;
- neighborhood candidate/anchor swap;
- quantifier polarity swap;
- universal/existential restriction lowering swap;
- evaluation deduplication failure;
- output symbol collision across points;
- replay omission of one point.

A silent change in point or evaluation identity is a contract failure even when the final solver status happens to remain unchanged.

## Non-goals

This contract does not require:

- native execution of arbitrary quantified formulas;
- multiple model outputs;
- multiple models;
- general preprocessing encoding;
- partial anchors;
- distributed or remote point resolution;
- named multiple anchor sources;
- categorical neighborhood semantics beyond declared backend capability.

## Related decisions and specifications

- ADR-0017 — First-Class Points, Lexical Bindings, and Point-Indexed Model Evaluations
- `language/points-anchors-and-evaluations.md`
- `testing/point-binding-evaluation-test-matrix.md`
