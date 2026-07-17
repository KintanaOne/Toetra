# Verification Runtime

> Status: Implemented for anchors, grouped evidence, and multi-point replay

## Public execution

```python
session = verify(
    specification,
    model=model_or_path,
    dataset=optional_dataset,
    schema=optional_schema,
    anchor_source=optional_source,
    anchor_resolver=optional_resolver,
)
```

`dataset` supports model/schema introspection and, when no explicit anchor mechanism is supplied, may also be reused as the default source for `ref(...)`. `anchor_source` or `anchor_resolver` always wins.

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

JSON reporting uses `forml.verification-report` schema version 2 and serializes points explicitly. Text, HTML, and Jupyter renderers group values by point.

## Replay

`finding.replay()` reconstructs every referenced point in declaration order, calls the real estimator once per point, compares formal and concrete outputs, and reevaluates the canonical restriction and assertion.

Multi-point replay exposes:

```python
replay.inputs_by_point
replay.backend_outputs_by_point
replay.model_outputs_by_point
replay.relation_satisfied
replay.assertion_satisfied
replay.to_records()
replay.to_dataframe()
```

Flat replay properties are intentionally rejected when several points make them ambiguous.

## Runtime boundaries

- the model must expose compatible prediction behavior;
- point inputs must be reconstructible in `ModelSchema` order;
- preprocessing remains outside V1 unless already embodied in a future supported encoder;
- alternating quantifiers are rejected before execution;
- replay is unavailable when required point values or model outputs are incomplete.
