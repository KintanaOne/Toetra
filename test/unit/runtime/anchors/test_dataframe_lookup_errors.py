from __future__ import annotations

import pandas as pd
import pytest

from toetra._runtime import (
    AnchorLookupRequest,
    AnchorResolutionError,
    DataFrameAnchorResolver,
)
from toetra._compiler.semantic.symbols.point import PointLiteral
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target="score",
        task="regression",
    )


def _request() -> AnchorLookupRequest:
    return AnchorLookupRequest(
        name="row",
        key="id",
        value=PointLiteral(value="R-42", dtype=EnumDataType.STRING),
    )


def test_run_ref_002_rejects_missing_match() -> None:
    resolver = DataFrameAnchorResolver(pd.DataFrame({"id": ["R-41"], "a": [1.0]}))

    with pytest.raises(AnchorResolutionError) as caught:
        resolver.resolve((_request(),), schema=_schema())

    assert caught.value.code == "ANCHOR_MATCH_NOT_FOUND"
    assert caught.value.anchor_name == "row"


def test_run_ref_003_rejects_non_unique_match() -> None:
    resolver = DataFrameAnchorResolver(
        pd.DataFrame({"id": ["R-42", "R-42"], "a": [1.0, 2.0]})
    )

    with pytest.raises(AnchorResolutionError) as caught:
        resolver.resolve((_request(),), schema=_schema())

    assert caught.value.code == "ANCHOR_MATCH_NOT_UNIQUE"


def test_run_ref_004_rejects_missing_lookup_key_column() -> None:
    resolver = DataFrameAnchorResolver(pd.DataFrame({"a": [1.0]}))

    with pytest.raises(AnchorResolutionError) as caught:
        resolver.resolve((_request(),), schema=_schema())

    assert caught.value.code == "ANCHOR_KEY_MISSING"
