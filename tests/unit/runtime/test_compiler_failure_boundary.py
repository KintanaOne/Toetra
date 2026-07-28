from __future__ import annotations

from pathlib import Path

import pytest

import toetra._runtime.api as runtime_api
from toetra import VerificationConfigurationError, verify
from toetra._compiler.builder.errors import BuilderError
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.semantic.errors.errors import SemanticError
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema

_VALID_SOURCE = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0 => x0.a <= 7.0
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


def test_verify_normalizes_syntax_failure_and_preserves_private_cause() -> None:
    source = _VALID_SOURCE.replace("forall x0", "forall")

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(source, schema=_schema())

    error = caught.value
    assert error.stage == "syntax"
    assert error.code.startswith("PARSER_")
    assert error.line is not None
    assert error.column is not None
    assert error.hint is not None
    assert error.path is None
    assert isinstance(error.__cause__, ParserError)


def test_verify_reports_specification_path_for_syntax_failure(
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid.toetra"
    path.write_text(_VALID_SOURCE.replace("forall x0", "forall"), encoding="utf-8")

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(path, schema=_schema())

    assert caught.value.path == str(path)


def test_verify_normalizes_builder_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_structure(_tree: object) -> None:
        raise BuilderError(
            "Malformed property structure",
            code="BUILDER_MALFORMED_PROPERTY",
            hint="Complete the property.",
        )

    monkeypatch.setattr(runtime_api, "parse_program", reject_structure)

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(_VALID_SOURCE, schema=_schema())

    error = caught.value
    assert error.stage == "builder"
    assert error.code == "BUILDER_MALFORMED_PROPERTY"
    assert error.hint == "Complete the property."
    assert isinstance(error.__cause__, BuilderError)


def test_verify_normalizes_semantic_failure_without_calling_it_syntax() -> None:
    source = _VALID_SOURCE.replace("x0.a", "y.a")

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(source, schema=_schema())

    error = caught.value
    assert error.stage == "semantic"
    assert error.code.startswith("SEMANTIC_")
    assert error.line is not None
    assert error.column is not None
    assert isinstance(error.__cause__, SemanticError)
