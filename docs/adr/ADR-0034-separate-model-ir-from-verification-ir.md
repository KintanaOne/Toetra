# ADR-0034 — Separate Model IR from Verification IR

> Status: Accepted and implemented for the affine runtime path
>
> Date: 2026-08-14
>
> Scope: ModelBridge, model representation, compiler model lowering, IR2,
> backend boundary

## Context

ADR-0008 established `ModelSchema` as the normalized bridge between framework
models and Toetra. ADR-0024 later established an explicit model-semantic
lowering boundary for declarative output observables.

The current affine implementation still leaves one architectural responsibility
implicit.

Affine coefficients, intercepts, and ordered features are normalized through
model metadata and consumed by model encoders that directly construct
verification IR2 objects. Those IR2 objects do not represent a model independently
of a verification task: they represent constraints induced by explicit model
evaluations inside that task.

For example, these are distinct artifacts:

```text
f(x) = w.x + b
```

and:

```text
output(model, point_x) = w.point_x + b
```

The first describes how an affine model computes. The second describes what
that computation implies for a particular symbolic evaluation.

This distinction must become explicit before adding structurally richer model
families such as decision trees and ensembles.

## Decision

Toetra will introduce an explicit backend-neutral **Model Intermediate
Representation (Model IR)** owned by the model subsystem.

Model IR and compiler verification IR are distinct artifacts with distinct
ownership and lifecycles.

The target flow is:

```text
framework model artifact
        |
        v
loader / detector / introspector
        |
        +---------------------> ModelSchema
        |
        v
Model IR construction
        |
        v
Model IR
        |
        | model + evaluation lowering
        v
Verification IR2 model constraints
        |
        | backend translation
        v
backend-native representation
```

### ModelSchema responsibility

`ModelSchema` remains the normalized bridge defined by ADR-0008.

It describes what Toetra can observe about a model and what interface the model
exposes, including model/framework identity, ordered features, task, typed
outputs, compatibility information, and relevant provenance metadata.

`ModelSchema` is not the canonical representation of supported computational
model structure.

A valid `ModelSchema` may exist even when Toetra has no supported Model IR for
that model family.

### Model IR responsibility

Model IR describes how a supported model computes independently of:

- the source ML framework;
- a particular Toetra property;
- a particular symbolic point or model evaluation;
- IR2 logical normalization;
- a particular verification backend.

Model IR is model-scoped and reusable across all symbolic evaluations requested
by a verification task.

The initial target family is affine. Future families may introduce tree and
ensemble Model IRs.

### Verification IR2 responsibility

Model-related IR2 objects remain owned by the compiler.

They represent the logical constraints induced by model semantics for the
specific evaluations required by a verification task. They may therefore
contain point identities, model-evaluation identities, comparison operators,
logical atoms, assumptions, and canonical model quantities.

Existing affine model constraints under:

```text
src/toetra/_compiler/ir/ir2/model/
```

remain verification IR and are not reclassified as Model IR.

### Compiler model-lowering responsibility

The compiler owns the transformation:

```text
Model IR
+ ModelSchema / model-family semantics
+ required ModelEvaluationIR values
        |
        v
Verification IR2 model assumptions and constraints
```

This transformation is distinct from framework-specific Model IR construction.

The former `_models/encoder` responsibility is split between Model IR
construction owned by the model subsystem and model-to-verification lowering
owned by the compiler. Legacy encoders remain only as an explicit compatibility
seam for advanced integrations and equivalence testing.

### Package ownership target

The intended ownership is:

```text
src/toetra/_models/ir/
    Model IR definitions

src/toetra/_models/ir_builder/
    framework/schema normalization into Model IR

src/toetra/_compiler/model_lowering/
    Model IR + evaluations -> Verification IR2

src/toetra/_compiler/ir/ir2/model/
    verification-specific model constraints

src/toetra/_backends/
    Verification IR2 -> backend-native representation
```

Concrete class APIs are intentionally deferred to implementation patches.

### Dependency invariants

The following dependency direction is normative:

```text
framework adapters
       |
       v
ModelSchema / Model IR
       |
       v
compiler model lowering
       |
       v
Verification IR2
       |
       v
backend translation
```

In particular:

- `_models.ir` must not depend on `_compiler` or `_backends`;
- `_models.ir_builder` must not depend on `_compiler` or `_backends`;
- compiler model lowering may depend on `_models.ir`, model schemas,
  model-semantic profiles, and compiler IR;
- backends consume verification IR and must not interpret Model IR directly;
- Model IR must not contain framework-native estimators or backend-native
  expressions.

These invariants will be enforced by architecture tests once the migration is
complete.

### Relationship with model-semantic lowering

ADR-0024 remains authoritative for translating public observables such as
labels and probabilities into canonical model-family quantities.

The responsibilities are distinct:

```text
Model-semantic lowering:
    What does this user-visible observable mean for this model family?

Model IR:
    How does this supported model compute?

Compiler model lowering:
    What verification constraints does that computation impose for the
    required evaluations?
```

## Rationale

Making model computation a first-class typed artifact:

- removes computational structure from generic metadata as the long-term source
  of truth;
- prevents framework adapters from owning verification semantics;
- prevents backends from interpreting framework or model-family structure;
- allows one normalized model representation to be reused across symbolic
  evaluations;
- gives decision trees and ensembles a natural architectural home;
- allows multiple frameworks to target the same model-family representation;
- makes the model boundary explicit in documentation and testing.

## Consequences

### Positive

- Model computation becomes an explicit, testable artifact.
- `ModelSchema`, Model IR, Verification IR2, and backend representations have
  distinct responsibilities.
- Future tree and ensemble support does not need to encode structure in schema
  metadata or backend-specific forms.
- Model-family support can evolve independently across frameworks and backends.

### Negative

- The model pipeline gains one explicit intermediate layer.
- The existing `_models/encoder` subsystem must be split and eventually removed
  or replaced.
- Runtime planning and numeric compatibility descriptors may require migration.
- Additional unit, equivalence, and architecture tests are required.

## Migration constraints

This ADR is a contract freeze, not a behavioral change.

The migration must:

- preserve the public `1.0.0rc4` verification behavior;
- introduce Model IR before switching the runtime pipeline;
- keep the legacy model-encoding path until semantic equivalence is
  demonstrated;
- compare legacy and new IR2 model assumptions before removing the old path;
- avoid introducing Model IR into backend translators;
- avoid embedding the complete Model IR inside `VerificationTaskIR2`;
- remove legacy computational metadata only after no executable path depends on
  it.

Tree and ensemble support are outside the migration itself.

## Alternatives considered

### Keep computational parameters in `ModelSchema.metadata`

Rejected as the long-term representation because generic metadata does not
provide a typed and extensible computational contract for richer model families.

### Treat `ModelSchema` itself as Model IR

Rejected because describing a model interface and representing its computation
are different responsibilities. Toetra must remain able to inspect a model
whose computation it cannot yet formally encode.

### Move existing affine IR2 classes into `_models`

Rejected because the existing affine IR2 objects are evaluation-specific
logical constraints and belong to verification IR.

### Let each backend interpret Model IR

Rejected because it would duplicate model-family semantics at the backend
boundary and couple backends to model representation details.

### Delay Model IR until tree support

Rejected because the current affine path already exposes the missing boundary.
Defining it first prevents the next model family from hardening the ambiguity.

## Relationship to existing ADRs

ADR-0008 remains accepted. `ModelSchema` remains the normalized bridge used for
model-aware validation and compatibility; this ADR clarifies that it is not the
complete computational representation of supported model families.

ADR-0024 remains accepted. Model-semantic lowering remains distinct from both
Model IR construction and compiler model lowering.

## Impact on Toetra

Toetra gains an explicit model representation boundary:

```text
Model artifact
    |
    +--> ModelSchema -----------+
    |                           |
    +--> Model IR --------------+--> compiler lowering --> IR2 --> backend
```

The affine implementation now satisfies the migration gate:

- artifact-backed sklearn models construct `AffineModelIR` directly from the
  fitted estimator;
- schema-only execution constructs the same IR through a documented legacy
  metadata compatibility builder;
- compiler-owned affine lowering consumes Model IR and requested evaluations;
- regression and binary-logistic assumptions are compared structurally with
  the legacy encoders;
- the default runtime uses Model IR construction and compiler lowering;
- an explicitly supplied `model_encoder_factory` retains the previous advanced
  integration seam;
- architecture tests prevent Model IR from depending on compiler/backends and
  prevent backends from consuming Model IR directly.

Tree and ensemble families remain future additions under the same accepted
boundary; they are not required to consider the affine migration complete.
