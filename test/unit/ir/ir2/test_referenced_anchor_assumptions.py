from __future__ import annotations

import pytest

from dsl.ir.ir2.errors import InvalidIR2InputError
from dsl.ir.ir2.run_ir2 import run_ir2_with_model_schema
from dsl.semantic.symbols.point import (
    AnchorResolutionProvenance,
    PointLiteral,
    ResolvedAnchorBinding,
    frozen_mapping,
)
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema

_SOURCE = """
model := "linear.joblib"
target := score

anchor row := ref(key = "id", value = "R-42")

[BOUND]:
check_at row => target <= 3.0 using Z3
"""


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )


def _resolution() -> ResolvedAnchorBinding:
    lookup = PointLiteral(value="R-42", dtype=EnumDataType.STRING)
    return ResolvedAnchorBinding(
        concrete_values=frozen_mapping(
            {"a": PointLiteral(value=1.0, dtype=EnumDataType.FLOAT)}
        ),
        provenance=AnchorResolutionProvenance(
            key="id",
            lookup_value=lookup,
            source_kind="dataframe",
            source_reference=None,
            row_index="0",
        ),
    )


def test_referenced_anchor_resolution_becomes_point_owned_assumption() -> None:
    task = run_ir2_with_model_schema(
        _SOURCE,
        schema=_schema(),
        resolved_anchors={"row": _resolution()},
    )[0]

    point = task.point_mappings[0].ir_point
    assert point.name == "row"
    assert point.concrete_values[0].feature == "a"
    assert point.resolution is not None
    assert point.resolution.key == "id"
    assert any(
        assumption.metadata.get("origin") == "referenced_anchor"
        for assumption in task.assumptions
    )


def test_unresolved_referenced_anchor_cannot_reach_ir2() -> None:
    with pytest.raises(InvalidIR2InputError, match="without runtime resolution"):
        run_ir2_with_model_schema(_SOURCE, schema=_schema())
