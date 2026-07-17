# Open Questions

> Status: Active after Patch 15 closure

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
