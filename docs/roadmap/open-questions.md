# Open Questions

> Status: Active after Patch 21.0 specification freeze

Patch 15 resolved the language and architecture questions around points, scopes, anchors, quantifier nesting, multiple evaluations, reporting, and replay. Those decisions are normative in ADR-0017 and are no longer open.

## Closed by Patch 15

- points are first-class symbols in a composed lexical environment;
- anchor bindings are inline, referenced, or runtime-resolved;
- `dataset` may be the default anchor source, with explicit overrides;
- binder lists expand left to right and indentation is non-semantic;
- one scalar target is indexed by input point;
- bare references require exactly one eligible default point;
- `where` and natural `neighborhood` have quantifier-sensitive lowering;
- `check_at` selects a declared anchor;
- new `at` is universal local sugar;
- pairwise properties use explicit points and relations;
- alternating quantifiers are preserved and capability-rejected;
- ModelBridge emits one equation per requested evaluation;
- Z3 uses distinct point-aware symbols;
- JSON schema v2 and grouped replay are the public multi-point contract;
- legacy provisional forms remain parseable only for migration diagnostics;
- `SemanticScope` is compatibility metadata, not semantic authority.


## Closed by Patch 21.0

- `target` remains the user-facing output-port reference but no longer implies one
  directly addressable scalar in the target architecture;
- classification users select `label` or `probability(label)` explicitly;
- logits, decision functions, generic scores, framework methods, class indices,
  and backend symbols are not DSL observables;
- model evaluation identity is separate from observable identity;
- model-family semantic lowering is explicit, provenanced, and occurs before
  backend translation;
- the first semantic family is binary logistic affine classification;
- the first concrete bridge is direct fitted binary sklearn `LogisticRegression`;
- the native decision policy uses probability `> 0.5`, equivalently oriented
  decision value `> 0`, with equality assigned to the negative label;
- custom/tuned thresholds, wrappers, calibration, pipelines, and multiclass are
  outside the initial profile;
- a property probability threshold is distinct from the model's native decision
  threshold;
- probability threshold materialization follows ADR-0018 and may never use an
  unqualified silent float approximation;
- ADR-0022 and `1.0.0rc1` remain unchanged until the final Patch 21 release gate.

## Patch 21 implementation questions

The following are implementation choices bounded by the accepted contracts, not
open semantic questions:

- the exact Python discriminated-union shape for typed output schemas;
- the temporary compatibility-alias lifetime for scalar-target class names;
- the rational enclosure algorithm and refinement precision for general logit
  thresholds;
- whether classification report evolution requires JSON v6 or can remain a
  strictly additive v5 extension;
- the exact internal names for model quantities and lowering evidence objects.

## Remaining V1 stabilization questions

### Public error taxonomy

Which parser, semantic, model, routing, backend, and runtime exceptions should cross the public `forml.verify` boundary unchanged, and which should be wrapped in stable user-facing errors?

### Solver resource policy

What default timeout, cancellation, and resource metadata should V1 expose without changing logical result semantics?

### Release packaging

Which examples, notebooks, JSON schemas, and compatibility promises are required for the first public V1 release?

### Mutation and property-based coverage

Which compiler and runtime invariants should be promoted first into Miova campaigns after the deterministic Patch 15 suite?

## Post-V1 research questions

- rich model encoders and preprocessing-aware verification;
- native execution of alternating quantifiers;
- categorical and structured inputs;
- multi-output and multi-model properties;
- additional neighborhood metrics and optimization objectives;
- backend orchestration beyond Z3.
