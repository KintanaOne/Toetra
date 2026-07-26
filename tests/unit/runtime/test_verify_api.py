from __future__ import annotations

from pathlib import Path

import pytest

from toetra._runtime.errors import (
    BackendRunnerNotRegisteredError,
    VerificationConfigurationError,
)
from toetra._runtime.backends import BackendRunnerRegistry
from toetra._runtime.api import verify
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema

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
    with pytest.raises(VerificationConfigurationError, match="Toetra header target"):
        verify(_SOURCE, model="model.joblib", target="other_score")


def test_verify_requires_runner_for_selected_backend() -> None:
    with pytest.raises(BackendRunnerNotRegisteredError, match="Z3"):
        verify(
            _SOURCE,
            schema=_schema(),
            runner_registry=BackendRunnerRegistry(),
        )


def test_verify_treats_missing_toetra_string_as_a_file_path() -> None:
    with pytest.raises(FileNotFoundError, match="Toetra specification"):
        verify("missing.toetra", schema=_schema())


@pytest.mark.parametrize("specification", ["legacy.forml", Path("legacy.forml")])
def test_verify_rejects_legacy_forml_extension(
    specification: str | Path,
) -> None:
    with pytest.raises(VerificationConfigurationError, match=r"\.toetra"):
        verify(specification, schema=_schema())
