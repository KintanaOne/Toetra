# Model IR Contract

> Status: Stabilized for affine structure, sklearn construction, and default
> runtime adoption
>
> Scope: ModelBridge, model representation, model IR construction, compiler
> model lowering

## Purpose

Model IR is Toetra's normalized, framework-agnostic and backend-agnostic
representation of supported model computation.

A Model IR answers:

> How does this model compute?

It does not describe the complete model interface, a verification property, a
specific symbolic evaluation, or a backend encoding.

The Model IR boundary is defined architecturally by ADR-0034.

## Responsibilities

The model-related representations have distinct responsibilities:

| Artifact | Responsibility |
|---|---|
| `ModelSchema` | Describe what the model exposes to Toetra. |
| Model IR | Describe how the supported model computes. |
| Model semantic profile | Define the meaning of model-family observables and canonical quantities. |
| Verification IR2 | Represent constraints induced by model computation for specific symbolic evaluations. |
| Backend representation | Represent verification constraints in a concrete solver or verifier. |

Model IR must remain independent from verification-task state.

It must not contain:

- symbolic points;
- `ModelEvaluationIR` values;
- verification properties;
- logical polarity;
- IR2 assumptions or constraints;
- backend-native expressions;
- framework-native estimator objects.

## General Model IR invariants

Every Model IR must satisfy the following invariants.

| Invariant | Requirement |
|---|---|
| Framework independence | The representation must not depend on sklearn, XGBoost, PyTorch, TensorFlow, ONNX runtime objects, or another source framework API. |
| Backend independence | The representation must not depend on Z3 or another verification backend. |
| Verification independence | The representation must not depend on a particular property or symbolic evaluation. |
| Structural validity | An instantiated Model IR must represent a structurally valid computation for its model family. |
| Determinism | Equivalent source models must produce deterministic normalized representations. |
| Immutability | A successfully constructed Model IR and all computation-defining values reachable from it must not be mutable. |
| Explicit computation | Information required to define the computation must use typed representation fields rather than generic metadata. |

A Model IR should be valid by construction whenever practical.

Invalid source artifacts must be rejected at the Model IR construction boundary
rather than represented as partially valid Model IR objects.

## Family-specific invariants

### Affine Model IR

An affine model represents a computation of the form:

```text
f(x) = Σ wi * xi + b
```

The normalized representation consists of:
- an ordered immutable sequence of affine terms;
- one affine bias.

An affine term associates exactly one normalized feature identifier with one
```text
AffineTerm = (feature identifier, coefficient)
```
Conceptually:
```text
AffineModelIR
├── terms
│   ├── (feature_0, coefficient_0)
│   ├── (feature_1, coefficient_1)
│   └── ...
└── bias
```

The feature/coefficient association is explicit. Consumers must not reconstruct
that association from separate positional feature and coefficient collections.

| Invariant                  | Requirement                                                                               | Rationale                                                                                      |
| -------------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Explicit term association  | Every affine term associates exactly one feature identifier with exactly one coefficient. | Prevent feature/coefficient synchronization and positional ambiguity.                          |
| Unique feature identifiers | A feature identifier must not occur more than once in the normalized term sequence.       | Preserve one unambiguous coefficient per input dimension.                                      |
| Stable term order          | The affine term sequence must preserve a deterministic order.                             | Reproducible equality, serialization, provenance, and lowering.                                |
| Immutable term sequence    | Neither the term sequence nor an individual affine term may change after construction.    | Prevent changes to model semantics after normalization.                                        |
| Finite coefficients        | Every coefficient must be a finite numeric value.                                         | `NaN` and infinite coefficients do not represent the supported real-valued affine computation. |
| Finite bias                | The affine bias must be finite.                                                           | Preserve a valid real-valued affine computation.                                               |


The order of affine terms is part of the normalized representation, even
though mathematical addition is commutative.

This ordering requirement exists for deterministic representation and does not
change the mathematical semantics of:

```text
Σ wi * xi
```
An empty affine term sequence is not universally forbidden by this contract.

Mathematically:

```text
f(x) = b
```

is a valid constant affine function.

Individual framework adapters or supported model profiles may impose stronger
requirements if their source model contract requires one or more features.

### Tree Model IR

Tree Model IR is not yet implemented.

Its expected invariant categories include:

| Invariant category  | Expected requirement                                                |
| ------------------- | ------------------------------------------------------------------- |
| Node identity       | Every referenced node must exist.                                   |
| Root                | Exactly one valid root must exist.                                  |
| Acyclicity          | The tree must contain no cycle.                                     |
| Reachability        | Every executable node must be reachable from the root.              |
| Branch completeness | Internal decision nodes must define the required outgoing branches. |
| Feature references  | Decision features must refer to valid normalized inputs.            |
| Leaf validity       | Leaves must define valid terminal values or quantities.             |

Exact requirements are deferred until Tree Model IR is designed.

### Tree Ensemble Model IR

Tree Ensemble Model IR is not yet implemented.

Its expected invariant categories include:

| Invariant category      | Expected requirement                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------ |
| Component validity      | Every component tree must satisfy the Tree Model IR contract.                              |
| Aggregation definition  | The ensemble aggregation operation must be explicit.                                       |
| Component compatibility | Tree outputs must be compatible with the declared aggregation rule.                        |
| Deterministic ordering  | Component ordering must be stable when it affects normalized representation or provenance. |

Exact requirements are deferred until Tree Ensemble Model IR is designed.

## Numeric validity

Model IR numeric invariants concern **model parameters**, not runtime input data.

For example:

| Situation                                                               | Ownership                                             |
| ----------------------------------------------------------------------- | ----------------------------------------------------- |
| Input dataset contains `NaN`                                            | Dataset, preprocessing, domain, or runtime validation |
| Symbolic input domain permits unsupported values                        | Semantic / verification-domain validation             |
| Source model coefficient contains `NaN`                                 | Model IR construction                                 |
| Source model coefficient contains `+inf` or `-inf`                      | Model IR construction                                 |
| Model IR coefficient is non-finite                                      | Model IR invariant violation                          |
| Model IR bias is non-finite                                             | Model IR invariant violation                          |
| Backend cannot faithfully represent a valid Model IR-derived constraint | Numeric compatibility / backend capability            |

The existence of valid preprocessing upstream does not weaken Model IR
invariants.

Model IR only guarantees that the normalized model computation itself satisfies
its representation contract.

## Error ownership

Errors should be rejected at the earliest layer that owns the violated contract.

```text
source model artifact
        |
        | unsupported or invalid source parameters
        X
Model IR construction
        |
        | invalid Model IR structure
        X
Model IR invariant validation
        |
        v
valid Model IR
        |
        | unsupported semantic/evaluation lowering
        X
compiler model lowering
        |
        v
Verification IR2
        |
        | unsupported backend representation
        X
backend compatibility / translation
```

Model IR construction errors must not be deferred to backend translation.

Likewise, Model IR must not attempt to validate unrelated runtime data or
verification-property semantics.

## Construction contract

Framework-specific adapters are responsible for constructing Model IR from
supported source models.

Conceptually:

```text
framework model
      +
ModelSchema
      |
      v
Model IR builder
      |
      v
Model IR
```

The builder may use framework-specific APIs and normalized schema information.

The resulting Model IR must not retain those framework-specific objects.

The normalized `ModelSchema` input is an immutable snapshot. A builder may use
its ordered features and typed output information, but it must neither mutate
the schema nor depend on later adapter/runtime changes.

During migration, existing normalized metadata may temporarily be used as an
input to Model IR construction. It must not remain the long-term canonical
representation of model computation.

The default artifact-backed sklearn path reads coefficients and intercepts
directly from the fitted model. Schema-only execution retains a dedicated
metadata compatibility builder so the RC4 contract remains executable, but
compiler lowering never reads those generic metadata values.

## Compiler consumption contract

The compiler consumes Model IR together with the semantic and evaluation
information required by the current verification task.

Conceptually:

```text
Model IR
    +
ModelSchema / model-family semantics
    +
ModelEvaluationIR values
    |
    v
compiler model lowering
    |
    v
Verification IR2 model constraints
```

A single Model IR may therefore be reused for multiple model evaluations.

Model IR itself must not be duplicated or specialized per symbolic point solely
to satisfy verification lowering.

For built-in affine routes this is the default runtime path. Supplying an
explicit legacy `model_encoder_factory` opts into the compatibility extension
seam and does not change the ownership of the built-in path.

## Equality and reproducibility

Model IR should support deterministic structural comparison.

Two normalized representations describing the same supported computation should
not differ merely because of:

* dictionary iteration order;
* framework-specific object identity;
* temporary runtime state;
* backend selection;
* verification-property selection.

Where ordering is part of the normalized representation, builders must preserve
or derive it deterministically.

## Metadata rule

Generic metadata must not be used to hide computation required by a Model IR.

For example, future representations should not rely on patterns such as:

```text
TreeModelIR.metadata["nodes"]
TreeModelIR.metadata["thresholds"]
TreeEnsembleModelIR.metadata["estimators"]
```

when those values are required to define the model computation.

Such information belongs in explicit typed fields of the corresponding Model IR.

Diagnostic or provenance metadata may exist outside the computational contract,
provided model semantics do not depend on it.

## Non-goals

This contract does not define:

* the Python API of every Model IR class;
* framework-specific extraction logic;
* public DSL syntax;
* model-semantic observable rewrites;
* verification IR2 structure;
* backend encodings;
* input-data preprocessing policy;
* missing-value semantics for datasets;
* tree or ensemble support before those representations are designed.

## Testing requirements

Each Model IR family must have unit tests covering:

1. valid construction;
2. every normative family invariant;
3. immutability;
4. deterministic equality or normalized representation;
5. rejection of structurally invalid states;
6. rejection of unsupported non-finite model parameters where applicable.

Model IR builders must additionally test that equivalent supported source models
produce the expected normalized Model IR.

For Affine Model IR, tests must additionally cover:

- preservation of affine term order;
- rejection of duplicate feature identifiers;
- rejection of non-finite coefficients;
- rejection of a non-finite bias;
- structural equality of equivalent normalized affine representations.

Architecture tests must eventually enforce that:

```text
_models/ir/**         does not import _compiler
_models/ir/**         does not import _backends
_models/ir_builder/** does not import _compiler
_models/ir_builder/** does not import _backends
_backends/**          does not consume _models/ir directly
```

## Evolution rule

Adding a new Model IR family requires:

1. defining its computational responsibility;
2. documenting its normative invariants in this contract;
3. implementing invariant tests;
4. defining source-model builders;
5. defining compiler lowering separately;
6. defining compatibility requirements before backend execution.

New model families must not weaken the separation between ModelSchema, Model IR,
Verification IR, and backend representations.

```
