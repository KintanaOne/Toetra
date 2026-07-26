from __future__ import annotations

import pandas as pd

from toetra._runtime.anchors import (
    AnchorLookupRequest,
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
        features={
            "a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT),
            "b": FeatureSchema(name="b", dtype=EnumDataType.INT),
        },
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
    )


def _request() -> AnchorLookupRequest:
    return AnchorLookupRequest(
        name="row",
        key="customer_id",
        value=PointLiteral(value="C-42", dtype=EnumDataType.STRING),
    )


def test_run_ref_001_resolves_one_complete_point_in_schema_order() -> None:
    frame = pd.DataFrame(
        {
            "customer_id": ["C-42"],
            "b": [7],
            "a": [1.5],
        }
    )

    resolved = DataFrameAnchorResolver(frame).resolve((_request(),), schema=_schema())

    binding = resolved["row"]
    assert tuple(binding.concrete_values) == ("a", "b")
    assert binding.concrete_values["a"].value == 1.5
    assert binding.concrete_values["a"].dtype is EnumDataType.FLOAT
    assert binding.concrete_values["a"].source_dtype == "float64"
    assert binding.concrete_values["b"].value == 7
    assert binding.concrete_values["b"].source_dtype == "int64"
    assert binding.provenance.source_kind == "dataframe"
    assert binding.provenance.row_index == "0"


def test_run_ref_006_lookup_metadata_is_not_projected_as_model_feature() -> None:
    frame = pd.DataFrame(
        {
            "customer_id": ["C-42"],
            "audit_note": ["manual-review"],
            "a": [1.5],
            "b": [7],
        }
    )

    binding = DataFrameAnchorResolver(frame).resolve((_request(),), schema=_schema())[
        "row"
    ]

    assert tuple(binding.concrete_values) == ("a", "b")
    assert "customer_id" not in binding.concrete_values
    assert "audit_note" not in binding.concrete_values
    assert binding.provenance.key == "customer_id"
    assert binding.provenance.lookup_value.value == "C-42"


def test_default_resolver_accepts_csv_path_and_retains_source_reference(
    tmp_path,
) -> None:
    source_path = tmp_path / "anchors.csv"
    pd.DataFrame({"customer_id": ["C-42"], "a": [1.5], "b": [7]}).to_csv(
        source_path, index=False
    )

    binding = DataFrameAnchorResolver(source_path).resolve(
        (_request(),), schema=_schema()
    )["row"]

    assert binding.provenance.source_kind == "csv"
    assert binding.provenance.source_reference == str(source_path.resolve())
