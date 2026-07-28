# Adding a framework adapter

> **Audience:** ModelBridge, compatibility, packaging, and replay maintainers
>
> **Boundary:** private built-in extension; no external discovery API in V1

A framework adapter converts a concrete model ecosystem into Toetra's
framework-neutral boundaries. It answers:

```text
How does Toetra obtain a truthful ModelSchema and concrete replay observation
from this framework?
```

It does not define DSL meaning and does not translate IR2 into a backend query.

## Reuse before extending

Determine whether the framework implements an existing model family.

- If yes, preserve the existing family and semantic profile. Add only the
  framework-specific descriptor, encoder implementation if parameter access
  differs, and runtime observer.
- If no, follow the [model-family guide](adding-model-family.md) as a separate
  workstream.
- If the framework object is merely sklearn-compatible, reuse is allowed only
  when feature order, outputs, decision policy, parameters, and numeric
  semantics are explicitly checked. API resemblance alone is not proof of
  equivalent behavior.

XGBoost illustrates the boundary: detection and introspection code can exist
without an encoder, compatible backend route, replay support, or public
end-to-end claim.

## Current integration points

| Stage | Current source boundary | Responsibility |
|---|---|---|
| Artifact loading | `src/toetra/_models/loader/` | deserialize a declared format only |
| Framework identity | `EnumModelFramework` | stable internal framework value |
| Detection | `ModelDetector.detect(...)` | map a loaded object to exactly one framework |
| Introspection dispatch | `IntrospectorFactory.INTROSPECTORS` | choose one `BaseIntrospector` |
| Normalization | framework introspector | produce `ModelSchema` and compatibility descriptor |
| Formal encoding | `ModelEncoderRegistry` | select encoder by framework and model type |
| Concrete observation | `ModelRuntimeObserver` and `ModelObserverRegistry` | normalize concrete predictions for replay |
| Numeric policy | compatibility registry | qualify source/encoder/backend semantics |
| Dependencies | `pyproject.toml` and release inventory | make install behavior explicit and reproducible |

Detection and introspection dispatch are source-defined in V1. Registering a
private object at runtime does not make an external framework package a
supported Toetra extension.

## Implementation sequence

### 1. Define the support envelope

Record exact framework versions or opsets, model classes, artifact formats,
devices, dtypes, input shapes, output shapes, and unsupported wrappers.

State whether Toetra reasons about:

- the concrete framework execution;
- an exported representation;
- an extracted mathematical abstraction;
- or only the declared semantic target.

This decision drives compatibility classification and reporting. Do not use the
framework name as a substitute for numeric semantics.

### 2. Choose the loading boundary

Add a loader only when Toetra owns deserialization of a new artifact format.
Loading must remain separate from framework detection and introspection.

A loader:

- selects by an unambiguous format policy;
- returns the concrete model object without inventing schema metadata;
- converts missing, corrupt, unsafe, or unsupported artifacts into the
  appropriate model-loading failure;
- does not call the backend or execute predictions.

If the existing pickle/joblib path already loads the object, do not add a
framework-named loader.

### 3. Add deterministic detection

Add the framework value to `EnumModelFramework` only with a real detection and
introspection path. Update `ModelDetector` so specific classes are checked
before broad compatibility bases.

Detection must:

- tolerate an absent optional dependency;
- map an object to zero or one framework;
- avoid file-extension inference;
- avoid importing heavy optional packages unless required;
- reject unsupported objects explicitly.

Test overlapping class hierarchies. A framework-specific estimator must not be
silently classified as generic sklearn merely because it inherits
`BaseEstimator`.

### 4. Normalize through an introspector

Implement `BaseIntrospector.introspect()` and register it in
`IntrospectorFactory.INTROSPECTORS`.

The resulting `ModelSchema` must contain:

- ordered transformed features with semantic and source dtypes;
- one explicit output name and typed output schema;
- normalized task and exact supported output observables;
- concrete `model_type`;
- namespaced framework metadata;
- a `FrameworkModelDescriptor` containing adapter id/version, model family,
  source execution profile, parameter/input/output dtypes, and numeric
  semantics.

Do not leave routing-critical facts only in free-form `metadata`. Reject
missing feature order, ambiguous targets, unsupported multi-output shapes,
unknown labels, custom decision policies, or inconsistent external schemas at
this boundary.

### 5. Connect formal encoding

If an existing encoder can consume the normalized schema without inspecting
framework objects, reuse it. Otherwise implement a framework-specific
`ModelEncoder` that emits the same family-level semantic target and register it
in `create_default_model_encoder_registry()`.

The encoder may read normalized parameters from `ModelSchema`; it must not call
`predict`, import a backend, or change public observable semantics.

An adapter that can build a schema but has no selected encoder is introspection
support only.

### 6. Add concrete replay observation

Implement `ModelRuntimeObserver` for the framework. `supports(...)` must be
narrow enough to avoid claiming incompatible schema/model pairs.

`observe(...)` must:

- consume features in normalized schema order;
- return `ModelObservation`, never framework-native arrays or tensors;
- expose exactly the regression value, labels, probabilities, and internal
  quantities promised by the schema/profile;
- handle device placement and scalar conversion deterministically;
- reject unavailable views with `ReplayUnavailableError`.

Register the observer in the default observer registry. Replay is concrete
evidence; it does not participate in proof or repair a missing compatibility
rule.

### 7. Register numeric compatibility

Add evidence-backed rules for every public
framework/model/encoder/backend combination. Rules must distinguish versions,
opsets, dtypes, devices, exported representations, and source profiles whenever
those facts can change the conclusion.

Never add a wildcard rule solely to make routing succeed. No match must stay
unsupported. If the proof applies only to an extracted exact-real abstraction,
use semantic-target-only scope and make that boundary visible in reports.

### 8. Package and expose deliberately

Decide whether the framework is:

- a required dependency for every installation;
- an optional extra;
- or used only through an exported artifact format.

Whichever policy is chosen, test both dependency-present and dependency-absent
behavior. A missing optional framework must not break `import toetra` or the
built-in V1 routes.

Only after the default detector, introspector, encoder, compatibility rule, and
observer agree may the public support matrix and profile be widened.

## Test matrix

| Layer | Minimum coverage | Existing location to mirror |
|---|---|---|
| Loading | format selection, missing/corrupt artifact, absent optional dependency | `tests/unit/model/test_loaders.py` |
| Detection | supported object, overlap precedence, generic rejection, dependency absent | `tests/unit/model/test_detector.py` |
| Introspection | ordered features, output schema, family, dtypes, versions, unsupported shapes | `tests/unit/model/test_*_introspector.py` |
| Encoder selection | exact model type, fallback behavior, unregistered model, descriptor | `tests/unit/model/encoder/` |
| Compatibility | version/profile match, no match, ambiguous rules, conclusion limits | `tests/unit/compatibility/` |
| Replay | normalized values, feature order, missing views, tolerance boundaries | `tests/unit/runtime/test_model_observer.py` |
| Integration | artifact → schema → IR2 with the intended family profile | `tests/integration/` |
| End to end | real serialized model through `verify(...)`, report, and replay | `tests/e2e/runtime/` |
| Packaging | clean import without optional dependency and clean installed-wheel route with it | release tests and `make release-check` |

Use a real fitted artifact in the release or end-to-end probe when public
support depends on serialization. Test an unsupported estimator from the same
framework so broad detection cannot create an accidental route.

## Exit checklist

- [ ] support envelope and source numeric meaning are documented;
- [ ] loading, detection, and introspection remain separate;
- [ ] `ModelSchema` is complete, ordered, typed, and framework-normalized;
- [ ] an encoder and semantic profile exist for every claimed model route;
- [ ] the runtime observer exposes every replay-required view;
- [ ] compatibility rules fail closed outside the declared envelope;
- [ ] absent optional dependencies do not break core installation/import;
- [ ] default factories select the adapter without test-only injection;
- [ ] unit, contract, integration, end-to-end, clean-install, and release gates pass.
