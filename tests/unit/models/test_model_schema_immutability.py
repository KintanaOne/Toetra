from dataclasses import FrozenInstanceError, replace
from typing import Any, cast

import pytest

from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.metadata import FrozenMetadataMap
from toetra._models.schema.model_schema import ModelSchema


def _schema(
    *,
    features: dict[str, FeatureSchema] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features=features
        or {"age": FeatureSchema(name="age", dtype=EnumDataType.FLOAT)},
        output_name="score",
        task="regression",
        metadata=metadata,
    )


def test_feature_schema_is_frozen() -> None:
    feature = FeatureSchema(name="age", dtype=EnumDataType.FLOAT)

    with pytest.raises(FrozenInstanceError):
        feature.nullable = True  # type: ignore[misc]


def test_model_schema_fields_are_frozen() -> None:
    schema = _schema()

    with pytest.raises(FrozenInstanceError):
        schema.output_name = "risk"  # type: ignore[misc]


def test_features_are_detached_ordered_and_deeply_immutable() -> None:
    source = {"age": FeatureSchema(name="age", dtype=EnumDataType.FLOAT)}
    schema = _schema(features=source)

    source["income"] = FeatureSchema(name="income", dtype=EnumDataType.FLOAT)

    assert isinstance(schema.features, tuple)
    assert schema.feature_names == ("age",)
    with pytest.raises(TypeError):
        schema.features_by_name["income"] = source["income"]  # type: ignore[index]


def test_metadata_is_detached_ordered_and_deeply_immutable() -> None:
    source = {
        "linear": {
            "coef": [1.5, -2.0],
            "feature_names": ["age", "income"],
        }
    }
    schema = _schema(metadata=source)

    source["linear"]["coef"][0] = 99.0
    source["linear"]["feature_names"].append("score")

    linear = schema.metadata_by_name["linear"]
    assert isinstance(schema.metadata, tuple)
    assert isinstance(linear, FrozenMetadataMap)
    assert linear["coef"] == (1.5, -2.0)
    assert linear["feature_names"] == ("age", "income")
    with pytest.raises(TypeError):
        linear["coef"] = (99.0,)  # type: ignore[index]


def test_metadata_serialization_copy_cannot_mutate_schema() -> None:
    schema = _schema(metadata={"linear": {"coef": [1.5]}})

    serialized = schema.metadata_as_dict()
    serialized["linear"]["coef"][0] = 99.0

    linear = schema.metadata_by_name["linear"]
    assert isinstance(linear, FrozenMetadataMap)
    assert linear["coef"] == (1.5,)


def test_replace_preserves_immutable_collections() -> None:
    schema = _schema(metadata={"source": "test"})

    rebound = replace(schema, output_name="risk")

    assert schema.output_name == "score"
    assert rebound.output_name == "risk"
    assert rebound.features == schema.features
    assert rebound.metadata == schema.metadata


def test_feature_mapping_key_must_match_feature_name() -> None:
    with pytest.raises(ValueError, match="must match"):
        _schema(
            features={"age": FeatureSchema(name="income", dtype=EnumDataType.FLOAT)}
        )


def test_duplicate_feature_names_are_rejected() -> None:
    with pytest.raises(ValueError, match="Duplicate"):
        ModelSchema(
            framework=EnumModelFramework.SKLEARN,
            model_type="LinearRegression",
            features=(
                FeatureSchema(name="age", dtype=EnumDataType.FLOAT),
                FeatureSchema(name="age", dtype=EnumDataType.FLOAT),
            ),
            output_name="score",
            task="regression",
        )


def test_unsupported_mutable_metadata_value_is_rejected() -> None:
    with pytest.raises(TypeError, match="must normalize"):
        _schema(metadata={"unsafe": cast(Any, object())})
