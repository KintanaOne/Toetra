# Adding a model family

> **Audience:** compiler, ModelBridge, compatibility, reporting, and replay maintainers
>
> **Boundary:** private built-in extension; no public plugin API in V1

A model family is a framework-neutral mathematical contract. It answers:

```text
What function or decision rule is being verified?
```

It is not a Python estimator class, a serialization format, or a backend
encoding. `LinearRegression` is a framework model type; affine regression is
the family. A model implemented by two frameworks should share one family when
its normalized semantics are the same.

## Decide whether a new family is needed

Create a new family only when at least one of these changes:

- the mathematical function class;
- the public output observables or their meaning;
- the canonical internal quantities;
- the sound abstraction used for verification;
- the structural or numeric requirements placed on backends.

Do not create a new family merely for another framework, package version,
serialization format, fitted parameter dtype, or backend. Those dimensions
belong to compatibility descriptors and rules.

## Owned artifacts

| Concern | Current source boundary | Required output |
|---|---|---|
| Stable family/profile identity | `src/toetra/_models/families.py` | non-empty framework-neutral identifiers |
| Normalized outputs | `src/toetra/_models/schema/output_schema.py` | typed output contract and explicit availability |
| Source model description | `FrameworkModelDescriptor` via introspection or `framework_model_descriptor(...)` | family, versions, source profile, dtypes |
| Public-observable meaning | `src/toetra/_models/semantics/` | `ModelSemanticProfile` and lowering evidence |
| Profile dispatch | `ModelSemanticRegistry` | family-to-profile registration |
| Formal model equations | `src/toetra/_models/encoder/` | backend-independent `AssumptionIR2` values |
| Encoder dispatch | `ModelEncoderRegistry` | framework/model-type-to-encoder registration |
| Backend requirements | IR2 nodes and `IR2Requirements` | complete structural/numeric requirement set |
| Route soundness | `src/toetra/_compatibility/` | evidence-backed compatibility rule |
| User evidence | reporting and provenance builders | stable, backend-neutral explanation |
| Concrete comparison | `ModelRuntimeObserver` and replay | normalized observation of each public/internal view |

All these modules are private. Their names document the current implementation,
not a compatibility promise for external packages.

## Implementation sequence

### 1. Freeze the semantic contract

Write or amend an ADR and contract before adding dispatch code. Define:

- supported task, input/output arity, feature sorts, and parameter domain;
- exact public observables and rejected expressions;
- mathematical model equation or abstraction;
- internal quantities and why they are not public observables;
- native decision boundaries, tie behavior, and threshold rules;
- exact, over-approximating, under-approximating, or lossy meaning;
- which verification conclusions remain valid;
- evidence required to explain every lowering.

If the family requires new DSL syntax, treat that as a separate language
change. Extend the EBNF first, preserve source intent in AST/IR1, and do not make
the grammar imply executable support.

### 2. Normalize the schema

The framework introspector must construct one `ModelSchema` whose ordered
features, task, `output_name`, typed `output_schema`, and compatibility
descriptor agree.

Prefer an explicit `FrameworkModelDescriptor`. A fallback family of
`unknown:<task>:<model_type>` is fail-closed metadata, not a route definition.
Reject unsupported shapes and wrappers before they can be mistaken for the new
family.

### 3. Implement model-semantic lowering

Implement `ModelSemanticProfile.lower_task(...)` under
`src/toetra/_models/semantics/` and register it by family in
`create_default_model_semantic_registry()`.

The profile may rewrite public output observables into canonical
framework-neutral constraints. It must:

- preserve the original source formula for reporting and replay;
- reject unsupported operators, labels, thresholds, or combinations;
- attach stable profile and transformation versions;
- emit structured `SemanticLoweringEvidence`;
- introduce every requirement needed by later routing;
- avoid imports from concrete frameworks and backend packages.

Lowering occurs before final NNF. It must not hide a non-equivalent
transformation behind Boolean normalization.

### 4. Add a backend-independent encoder

Implement `ModelEncoder.encode(...)`. The encoder receives a normalized schema
and explicit `ModelEvaluationIR` identities; it must never infer points from a
legacy scope.

Each emitted assumption must:

- use `AssumptionSource.MODEL`;
- wrap an `NNFFormulaIR2`;
- connect each requested evaluation exactly once;
- preserve model, point, and output identity;
- use backend-neutral IR2 nodes;
- declare a `ModelEncoderDescriptor` with a stable encoder id, version, and
  semantic target.

Register built-in framework/model-type implementations in
`create_default_model_encoder_registry()`. If several frameworks share the
family, their encoders must target the same declared mathematical semantics or
use distinct compatibility rules.

### 5. Complete IR2 and capability requirements

Reuse existing IR2 atoms when their semantics are exact. Otherwise add a typed
IR2 node and update requirement extraction, validation, formatting, provenance,
and every backend translator that claims to support it.

Never encode a new family as an untyped backend string or smuggle a framework
object into IR2. A backend that cannot represent the new requirement must be
rejected by `BackendCapabilities.incompatibilities(...)`.

### 6. Register numeric compatibility

Add a rule to `create_default_numeric_compatibility_registry()` only after the
source descriptor, encoder descriptor, backend profile, and property
requirements can form a complete query.

The rule must declare:

- support status and semantic classification;
- semantic target and conclusion scope;
- evidence id and documentation reference;
- permitted conclusions;
- replay requirements;
- assumptions, preconditions, and diagnostics.

No-match, ambiguity, non-finite values, and unpermitted conclusions must remain
fail-closed. Regenerate and commit
`docs/generated/numeric-compatibility-matrices.md`.

### 7. Extend reporting and replay

Keep four roles distinct:

1. source observable;
2. internal model quantity;
3. formal backend assignment;
4. concrete framework observation.

Extend generic report models only when existing fields cannot represent the
evidence. JSON v6 changes must be additive and optional; an incompatible change
requires a later schema version.

Replay must reevaluate the preserved original property through a
`ModelRuntimeObserver`. Missing observables or internal quantities raise
`ReplayUnavailableError`; replay is never silently partial and never upgrades
an approximate universal result.

### 8. Publish only the complete route

Focused registry injection is useful for development, but public support
requires every default factory and end-to-end path to select the new
components. Update the supported-framework matrix, generated compatibility
matrices, public profile, release notes, examples, and exclusions together.

## Test matrix

| Layer | Minimum coverage | Existing location to mirror |
|---|---|---|
| Schema/introspection | family recognition, ordered features, output shape, dtype/source metadata, unsupported variants | `tests/unit/model/` |
| Semantic profile | accepted observable lowering, every rejection, boundaries, evidence versions, original-formula preservation | `tests/unit/model/semantics/` |
| Encoder | equations, one constraint per evaluation, point separation, missing/non-finite parameters, descriptor | `tests/unit/model/encoder/` |
| IR contract | NNF validity, requirements, pretty/golden stability, invalid-node rejection | `tests/unit/ir/` |
| Compatibility | exact rule, no match, ambiguity, conclusion policy, non-finite handling | `tests/unit/compatibility/` |
| Reporting/replay | all renderers, JSON, provenance, formal/concrete comparison, unavailable replay | `tests/unit/reporting/`, `tests/unit/runtime/` |
| Integration | introspection → lowering → IR2 and encoder/backend agreement | `tests/integration/` |
| End to end | proved and counterexample/witness cases through `verify(...)` | `tests/e2e/` |
| Public contract | supported and explicitly rejected public shapes | `tests/unit/public_contract/` |

Add adversarial boundary cases, not only a happy-path fitted model. At minimum
cover wrong arity, wrong output kind, unsupported wrapper, missing parameters,
non-finite values, feature-order mismatch, and an unregistered compatible-looking
model.

## Exit checklist

- [ ] family identity is framework-neutral and documented;
- [ ] schema, semantic profile, encoder, and IR2 requirements agree;
- [ ] unsupported variants fail before backend execution;
- [ ] compatibility rules justify every permitted conclusion;
- [ ] report, provenance, and replay expose the same route and evidence;
- [ ] default registries select the route without test-only injection;
- [ ] generated matrices and public documentation are current;
- [ ] unit, contract, integration, end-to-end, clean-install, and release gates pass.
