# Extension architecture

> **Status:** contributor guide for `1.0.0rc3`
>
> **Scope:** built-in extensions developed inside the Toetra repository

Toetra does not yet expose a stable third-party plugin API. The registries and
protocols described in these guides live below `toetra._*`; they are private
implementation boundaries, not supported user imports.

These boundaries still define how a built-in extension must be designed. They
keep framework integration, mathematical model meaning, and backend execution
separate.

## Choose the extension type first

| Change | Primary guide | It owns | It must not own |
|---|---|---|---|
| Add a new mathematical behavior, such as a tree ensemble or ReLU network | [Model family](adding-model-family.md) | normalized family identity, model semantics, formal encoding | framework loading or solver calls |
| Accept models from another library or artifact ecosystem | [Framework adapter](adding-framework-adapter.md) | detection, introspection, normalized schema, concrete observation | public DSL meaning or backend translation |
| Execute qualified IR2 with another solver or analyzer | [Backend](adding-backend.md) | capabilities, native translation, execution, normalized result | framework inspection or source parsing |

One product route can require more than one guide. For example, accepting a
PyTorch implementation of a previously unsupported ReLU family requires both a
framework adapter and a model-family implementation. A second framework that
implements an existing family should reuse that family's semantic profile
instead of creating framework-specific DSL meaning.

## The complete-route rule

An internal component is not an executable public route. Public support exists
only when the complete path agrees:

```text
artifact
→ framework detection and normalized ModelSchema
→ model-family semantic lowering
→ backend-independent model assumptions
→ IR2 requirements
→ backend capability and numeric qualification
→ backend execution
→ normalized result and report
→ concrete replay
```

The [public V1 profile](../public-v1-profile.md) is the source of truth for
routes that users may rely on. Vocabulary entries, enums, introspectors,
encoders, compatibility rows, or backend adapters can exist without widening
that profile.

## Route-readiness record

Before implementation, record one route matrix in the owning ADR or contract:

| Dimension | Required decision |
|---|---|
| Source | framework adapter, supported versions/opsets, artifact format, numeric execution profile |
| Model | framework-neutral family, task, input/output shape, exclusions |
| Semantics | public observables, canonical mathematical meaning, rejection cases |
| Encoding | encoder identity/version, emitted assumptions, introduced IR2 requirements |
| Backend | adapter, capabilities, numeric profile, execution controls |
| Soundness | compatibility classification, conclusion scope, permitted conclusions, replay requirements |
| Evidence | lowering, route, execution, report, and provenance fields |
| Validation | positive, negative, boundary, clean-install, and release coverage |

An unknown cell is not filled with a permissive default. It remains unsupported
or produces an explicit inconclusive result at the boundary that owns it.

## Registration has two levels

During focused tests, private registries can be constructed and injected into
internal runtime hooks. This proves a component in isolation.

A built-in route additionally requires registration in every applicable default
factory:

- model encoders in
  `src/toetra/_models/encoder/defaults.py`;
- model semantic profiles in
  `src/toetra/_models/semantics/registry.py`;
- runtime observers through
  `src/toetra/_models/runtime/sklearn_observer.py` or its future
  framework-neutral replacement;
- backend capabilities in
  `src/toetra/_backends/defaults.py`;
- backend runners in `src/toetra/_runtime/backends.py`;
- numeric rules in `src/toetra/_compatibility/defaults.py`.

Detection and introspection currently also use source-defined dispatch in
`ModelDetector` and `IntrospectorFactory`. There is no discovery mechanism for
external packages in V1.

## Definition of done

Every extension guide contains a focused test matrix. In addition, a route is
eligible for public support only when all of the following are true:

- unsupported variants fail before backend execution or return a justified
  `UNKNOWN`;
- the generated numeric compatibility matrices describe the route;
- all report formats and JSON v6 preserve its evidence without reinterpreting
  existing fields;
- replay uses the concrete framework object when the compatibility policy
  requires it;
- public documentation names exact supported versions, shapes, observables,
  exclusions, and conclusions;
- `make ci`, `make demo-check`, `make release-check`, and
  `make review-bundle-check` pass from a clean committed checkout.

Adding the route to the public profile is the final act of support, not the
first implementation step.
