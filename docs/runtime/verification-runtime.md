# Verification Runtime

> Status: Implemented for anchors, typed model-evaluation evidence, and multi-point replay

## Public execution

```python
session = verify(
    specification,
    model=optional_model_path,
    dataset=optional_dataset,
    schema=optional_schema,
    anchor_source=optional_source,
    anchor_resolver=optional_resolver,
)
```

The effective dataset comes from an explicit runtime override when present,
otherwise from the optional specification header. Header paths are relative to
the `.toetra` file; explicit paths are relative to the working directory. The
dataset supports model/schema introspection and, when no explicit anchor
mechanism is supplied, is reused as the default source for `ref(...)`.
`anchor_source` or `anchor_resolver` always wins.

## Anchor resolution

Referenced anchors are resolved before IR2. The default resolver accepts a `pandas.DataFrame` or CSV path, requires exactly one matching row, projects only declared model features, validates types, and preserves lookup provenance.

Inline anchors require no source. An unresolved referenced anchor cannot reach routing or Z3.

## Grouped results

Each finding exposes point-aware evidence:

```python
finding.points
finding.point_values
finding.output_values_by_point
```

Every point contains its binding kind, inputs, outputs, and provenance. Flat `input_values` and `output_values` remain available only for unambiguous one-point results.

JSON reporting uses the frozen `toetra.verification-report` schema version 6. Points remain explicit, and P21.9 adds an optional `model_evaluations` section for classification observables, internal technical quantities, and lowering traces. Text, HTML, and Jupyter renderers group these values by point and output port.

## Replay

`finding.replay()` reconstructs every referenced point in declaration order and delegates concrete evaluation to a framework-neutral `ModelRuntimeObserver`. It compares scalar outputs or classification labels/probabilities/internal quantities independently, then reevaluates the preserved original property. The initial sklearn observer uses `predict`, `predict_proba`, and `decision_function` behind that protocol.

Multi-point replay exposes:

```python
replay.inputs_by_point
replay.backend_outputs_by_point
replay.model_outputs_by_point
replay.relation_satisfied
replay.assertion_satisfied
replay.relation_consistent
replay.assertion_consistent
replay.to_records()
replay.to_dataframe()
replay.points["x"].evaluations
```

Flat replay properties are intentionally rejected when several points make them ambiguous.

Numeric ordering comparisons use three-valued replay semantics. When concrete
IEEE-754 values land within the absolute replay tolerance of an ordering
boundary, `relation_satisfied` or `assertion_satisfied` is `None` rather than a
false contradiction. The corresponding `*_consistent` property remains true
because the concrete replay is numerically indeterminate, not incompatible with
the exact-real backend result. Comparisons clearly outside the tolerance band
remain decisive.

## Runtime boundaries

- a registered runtime observer must support the model/schema pair;
- point inputs must be reconstructible in `ModelSchema` order;
- preprocessing reconstruction remains outside V1; inputs are expressed in the
  transformed feature space consumed by the encoded estimator;
- alternating quantifiers are rejected before execution;
- replay is unavailable when required point values or model outputs are incomplete.
