from __future__ import annotations

import pytest

from dsl.runtime import (
    BackendRunnerNotRegisteredError,
    BackendRunnerRegistry,
    VerificationConfigurationError,
    verify,
)
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema

_SOURCE = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target <= 7.0
    using Z3
"""


def _schema(*, target: str = "score") -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target=target,
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


def test_verify_rejects_schema_and_model_artifacts_together() -> None:
    with pytest.raises(VerificationConfigurationError, match="either 'schema'"):
        verify(_SOURCE, schema=_schema(), model="model.joblib")


def test_verify_rejects_header_and_schema_target_mismatch() -> None:
    with pytest.raises(VerificationConfigurationError, match="different outputs"):
        verify(_SOURCE, schema=_schema(target="other_score"))


def test_verify_rejects_explicit_target_different_from_header() -> None:
    with pytest.raises(VerificationConfigurationError, match="FORML header target"):
        verify(_SOURCE, model="model.joblib", target="other_score")


def test_verify_requires_runner_for_selected_backend() -> None:
    with pytest.raises(BackendRunnerNotRegisteredError, match="Z3"):
        verify(
            _SOURCE,
            schema=_schema(),
            runner_registry=BackendRunnerRegistry(),
        )


def test_verify_treats_missing_forml_string_as_a_file_path() -> None:
    with pytest.raises(FileNotFoundError, match="FORML specification"):
        verify("missing.forml", schema=_schema())
