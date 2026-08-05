from __future__ import annotations

from pathlib import Path

import pytest

from toetra import VerificationRuntimeError
from toetra._runtime.errors import (
    BackendRunnerNotRegisteredError,
    VerificationConfigurationError,
)
from toetra._runtime.backends import BackendRunnerRegistry
from toetra._runtime.api import _load_specification, _resolve_model, verify
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


def test_schema_output_is_rebound_to_the_effective_header_target() -> None:
    schema = _schema(target="other_score")
    loaded = _load_specification(_SOURCE)

    resolved = _resolve_model(
        loaded,
        model=None,
        dataset=None,
        target=None,
        schema=schema,
    )

    assert schema.output_name == "other_score"
    assert resolved.schema.output_name == "score"
    assert resolved.program.header.target == "score"


def test_explicit_target_rebinds_schema_and_effective_ast() -> None:
    schema = _schema()
    loaded = _load_specification(_SOURCE)

    resolved = _resolve_model(
        loaded,
        model=None,
        dataset=None,
        target="other_score",
        schema=schema,
    )

    assert schema.output_name == "score"
    assert resolved.schema.output_name == "other_score"
    assert resolved.program.header.target == "other_score"
    assert resolved.execution_context.target_overridden is True


def test_verify_requires_runner_for_selected_backend() -> None:
    with pytest.raises(VerificationRuntimeError, match="Z3") as caught:
        verify(
            _SOURCE,
            schema=_schema(),
            runner_registry=BackendRunnerRegistry(),
        )

    error = caught.value
    assert error.code == "BACKEND_RUNNER_NOT_REGISTERED"
    assert error.stage == "backend"
    assert error.hint is not None
    assert isinstance(error.__cause__, BackendRunnerNotRegisteredError)


def test_verify_treats_missing_toetra_string_as_a_file_path() -> None:
    with pytest.raises(VerificationConfigurationError) as caught:
        verify("missing.toetra", schema=_schema())

    error = caught.value
    assert error.code == "SPECIFICATION_NOT_FOUND"
    assert error.stage == "configuration"
    assert error.path == "missing.toetra"
    assert error.hint is not None


def test_verify_reports_invalid_specification_encoding(tmp_path: Path) -> None:
    path = tmp_path / "invalid.toetra"
    path.write_bytes(b"\xff")

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(path, schema=_schema())

    error = caught.value
    assert error.code == "SPECIFICATION_ENCODING_INVALID"
    assert error.stage == "configuration"
    assert error.path == str(path)
    assert error.hint is not None
    assert isinstance(error.__cause__, UnicodeDecodeError)


@pytest.mark.parametrize("specification", ["legacy.forml", Path("legacy.forml")])
def test_verify_rejects_legacy_forml_extension(
    specification: str | Path,
) -> None:
    with pytest.raises(VerificationConfigurationError, match=r"\.toetra"):
        verify(specification, schema=_schema())
