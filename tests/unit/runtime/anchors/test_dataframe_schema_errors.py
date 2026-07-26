from __future__ import annotations

import pandas as pd
import pytest

from toetra._runtime.anchors import (
    AnchorLookupRequest,
    DataFrameAnchorResolver,
)
from toetra._runtime.errors import AnchorResolutionError
from toetra._compiler.semantic.symbols.point import PointLiteral
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT),
            "count": FeatureSchema(name="count", dtype=EnumDataType.INT),
        },
        target="score",
        task="regression",
    )


def _request() -> AnchorLookupRequest:
    return AnchorLookupRequest(
        name="row",
        key="id",
        value=PointLiteral(value="R-42", dtype=EnumDataType.STRING),
    )


def test_run_ref_005_rejects_missing_model_feature() -> None:
    resolver = DataFrameAnchorResolver(pd.DataFrame({"id": ["R-42"], "a": [1.0]}))

    with pytest.raises(AnchorResolutionError) as caught:
        resolver.resolve((_request(),), schema=_schema())

    assert caught.value.code == "ANCHOR_FEATURE_MISSING"
    assert "count" in str(caught.value)


def test_run_ref_007_rejects_dtype_mismatch() -> None:
    resolver = DataFrameAnchorResolver(
        pd.DataFrame({"id": ["R-42"], "a": [1.0], "count": [1.5]})
    )

    with pytest.raises(AnchorResolutionError) as caught:
        resolver.resolve((_request(),), schema=_schema())

    assert caught.value.code == "ANCHOR_DTYPE_MISMATCH"
    assert "count" in str(caught.value)
