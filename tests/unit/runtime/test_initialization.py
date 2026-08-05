from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from tests.support.schemas import make_binary_classification_schema
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    RegressionOutputSchema,
    UnknownOutputSchema,
)
from toetra._runtime.errors import (
    VerificationConfigurationError,
    VerificationRuntimeError,
)
from toetra._runtime.initialization import (
    initialize_specification,
    render_starter_specification,
)
from toetra._runtime.preflight import (
    ValidationDiagnostic,
    ValidationLevel,
    ValidationResult,
)


def _regression_schema(*, feature_name: str = "a") -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            feature_name: FeatureSchema(
                name=feature_name,
                dtype=EnumDataType.FLOAT,
                nullable=False,
                source_dtype="float64",
            )
        },
        output_name="score",
        task="regression",
        output_schema=RegressionOutputSchema(
            value_dtype=EnumDataType.FLOAT,
            value_source_dtype="float64",
        ),
    )


def _valid_result() -> ValidationResult:
    return ValidationResult(
        requested_level=ValidationLevel.EXECUTABLE,
        completed_level=ValidationLevel.EXECUTABLE,
        valid=True,
        checks=("backend_translated",),
        property_count=1,
    )


def test_render_regression_starter_declares_all_supplied_artifacts() -> None:
    source = render_starter_specification(
        _regression_schema(),
        model_reference="../models/linear.joblib",
        dataset_reference="../data/reference.csv",
    )

    assert 'model := "../models/linear.joblib"' in source
    assert "target := score" in source
    assert 'dataset := "../data/reference.csv"' in source
    assert source.count("[LOGIC]:") == 1
    assert "target[sample] <= target[sample]" in source
    assert "integration only" in source
    assert "source: float64" in source
    assert source.endswith("\n")

    program = parse_program(parse_toetra_code(source))
    assert program.header.model == "../models/linear.joblib"
    assert program.header.target == "score"
    assert program.header.dataset == "../data/reference.csv"


def test_render_starter_omits_dataset_when_none_is_supplied() -> None:
    source = render_starter_specification(
        _regression_schema(),
        model_reference="linear.joblib",
    )

    assert "dataset :=" not in source


def test_render_classification_starter_uses_distinct_equal_inputs() -> None:
    source = render_starter_specification(
        make_binary_classification_schema(),
        model_reference="credit.joblib",
        dataset_reference="credit.csv",
    )

    assert "forall sample, duplicate" in source
    assert "where duplicate.income == sample.income" in source
    assert "target[sample].label == target[duplicate].label" in source
    assert source.count("[LOGIC]:") == 1


def test_initialize_validates_staged_declared_references_before_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    models = tmp_path / "models"
    policies = tmp_path / "policies"
    model = models / "linear model.joblib"
    dataset = models / "reference.csv"
    destination = policies / "generated.toetra"
    models.mkdir()
    model.write_bytes(b"trusted-model")
    dataset.write_text("a,score\n0,1\n", encoding="utf-8")
    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        lambda **_kwargs: _regression_schema(),
    )
    observed: dict[str, Any] = {}

    def validate(specification: Path, **kwargs: object) -> ValidationResult:
        observed["specification"] = specification
        observed["kwargs"] = kwargs
        source = specification.read_text(encoding="utf-8")
        assert 'model := "../models/linear model.joblib"' in source
        assert 'dataset := "../models/reference.csv"' in source
        assert not destination.exists()
        return _valid_result()

    result = initialize_specification(
        destination,
        model=model,
        dataset=dataset,
        target="score",
        validation_function=validate,
    )

    assert result.destination == destination.resolve()
    assert destination.read_text(encoding="utf-8") == result.source
    assert observed["kwargs"] == {"level": ValidationLevel.EXECUTABLE}
    assert not tuple(policies.glob(".generated.*.toetra"))


def test_existing_destination_is_rejected_before_model_loading(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "policy.toetra"
    model = tmp_path / "model.joblib"
    destination.write_text("original", encoding="utf-8")
    model.write_bytes(b"model")

    def fail_if_loaded(**_kwargs: object) -> ModelSchema:
        raise AssertionError("existing destinations must fail before model loading")

    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        fail_if_loaded,
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        initialize_specification(destination, model=model, target="score")

    assert raised.value.code == "INIT_DESTINATION_EXISTS"
    assert destination.read_text(encoding="utf-8") == "original"


def test_force_preserves_existing_destination_when_validation_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "policy.toetra"
    model = tmp_path / "model.joblib"
    destination.write_text("original", encoding="utf-8")
    model.write_bytes(b"model")
    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        lambda **_kwargs: _regression_schema(),
    )
    invalid = ValidationResult(
        requested_level=ValidationLevel.EXECUTABLE,
        completed_level=ValidationLevel.SEMANTIC,
        valid=False,
        checks=("semantic_validated",),
        diagnostic=ValidationDiagnostic(
            category="runtime",
            code="BACKEND_TRANSLATION_FAILED",
            stage="backend",
            message="translation failed",
        ),
    )

    with pytest.raises(VerificationRuntimeError) as raised:
        initialize_specification(
            destination,
            model=model,
            target="score",
            force=True,
            validation_function=lambda *_args, **_kwargs: invalid,
        )

    assert raised.value.code == "BACKEND_TRANSLATION_FAILED"
    assert destination.read_text(encoding="utf-8") == "original"
    assert not tuple(tmp_path.glob(".policy.*.toetra"))


def test_force_replaces_existing_destination_after_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "policy.toetra"
    model = tmp_path / "model.joblib"
    destination.write_text("original", encoding="utf-8")
    model.write_bytes(b"model")
    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        lambda **_kwargs: _regression_schema(),
    )

    initialize_specification(
        destination,
        model=model,
        target="score",
        force=True,
        validation_function=lambda *_args, **_kwargs: _valid_result(),
    )

    assert "Generated by `toetra init`" in destination.read_text(encoding="utf-8")


@pytest.mark.parametrize("role", ["model", "dataset"])
def test_init_rejects_destination_collision_with_input(
    role: str,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "artifact.toetra"
    model = destination if role == "model" else tmp_path / "model.joblib"
    dataset = destination if role == "dataset" else None
    model.write_bytes(b"model")
    if dataset is not None:
        dataset.write_text("a,score\n0,1\n", encoding="utf-8")

    with pytest.raises(VerificationConfigurationError) as raised:
        initialize_specification(
            destination,
            model=model,
            dataset=dataset,
            target="score",
        )

    assert raised.value.code == "INIT_DESTINATION_INPUT_COLLISION"


def test_init_rejects_feature_names_not_representable_in_dsl(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = tmp_path / "model.joblib"
    model.write_bytes(b"model")
    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        lambda **_kwargs: _regression_schema(feature_name="credit score"),
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        initialize_specification(
            tmp_path / "policy.toetra",
            model=model,
            target="score",
            validation_function=lambda *_args, **_kwargs: _valid_result(),
        )

    assert raised.value.code == "INIT_FEATURE_IDENTIFIER_UNSUPPORTED"


def test_init_rejects_non_toetra_destination_before_loading_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = tmp_path / "model.joblib"
    model.write_bytes(b"model")

    def fail_if_loaded(**_kwargs: object) -> ModelSchema:
        raise AssertionError("invalid destinations must fail before model loading")

    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        fail_if_loaded,
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        initialize_specification(
            tmp_path / "policy.txt",
            model=model,
            target="score",
        )

    assert raised.value.code == "INIT_DESTINATION_EXTENSION_INVALID"


def test_init_rejects_unsupported_model_task(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "policy.toetra"
    model = tmp_path / "model.joblib"
    model.write_bytes(b"model")
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="KMeans",
        features=_regression_schema().features,
        output_name="cluster",
        task="unknown",
        output_schema=UnknownOutputSchema(),
    )
    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        lambda **_kwargs: schema,
    )

    with pytest.raises(VerificationRuntimeError) as raised:
        initialize_specification(
            destination,
            model=model,
            target="cluster",
            validation_function=lambda *_args, **_kwargs: _valid_result(),
        )

    assert raised.value.code == "INIT_MODEL_TASK_UNSUPPORTED"
    assert not destination.exists()


def test_init_cleans_staged_file_when_validation_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "nested" / "policy.toetra"
    model = tmp_path / "model.joblib"
    model.write_bytes(b"model")
    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        lambda **_kwargs: _regression_schema(),
    )

    def fail_validation(*_args: object, **_kwargs: object) -> ValidationResult:
        raise VerificationRuntimeError(
            "validation failed",
            code="VALIDATION_FAILED",
            stage="backend",
        )

    with pytest.raises(VerificationRuntimeError) as raised:
        initialize_specification(
            destination,
            model=model,
            target="score",
            validation_function=fail_validation,
        )

    assert raised.value.code == "VALIDATION_FAILED"
    assert not destination.exists()
    assert not tuple(destination.parent.glob(".policy.*.toetra"))


def test_init_rejects_invalid_target_before_model_loading(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = tmp_path / "model.joblib"
    model.write_bytes(b"model")

    def fail_if_loaded(**_kwargs: object) -> ModelSchema:
        raise AssertionError("invalid targets must fail before model loading")

    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        fail_if_loaded,
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        initialize_specification(
            tmp_path / "policy.toetra",
            model=model,
            target="target",
        )

    assert raised.value.code == "INIT_TARGET_IDENTIFIER_UNSUPPORTED"


def test_init_rejects_symbolic_link_destination_even_with_force(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = tmp_path / "model.joblib"
    existing = tmp_path / "existing.toetra"
    destination = tmp_path / "policy.toetra"
    model.write_bytes(b"model")
    existing.write_text("original", encoding="utf-8")
    try:
        destination.symlink_to(existing)
    except (NotImplementedError, OSError):
        pytest.skip("symbolic links are unavailable in this environment")

    def fail_if_loaded(**_kwargs: object) -> ModelSchema:
        raise AssertionError("symbolic-link destinations must fail before loading")

    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        fail_if_loaded,
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        initialize_specification(
            destination,
            model=model,
            target="score",
            force=True,
        )

    assert raised.value.code == "INIT_DESTINATION_SYMLINK_UNSUPPORTED"
    assert existing.read_text(encoding="utf-8") == "original"
    assert destination.is_symlink()


def test_init_resolves_artifact_references_through_symbolic_parent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_root = tmp_path / "real"
    policies = real_root / "policies"
    artifacts = real_root / "artifacts"
    alias = tmp_path / "policy-alias"
    policies.mkdir(parents=True)
    artifacts.mkdir()
    try:
        alias.symlink_to(policies, target_is_directory=True)
    except (NotImplementedError, OSError):
        pytest.skip("symbolic links are unavailable in this environment")

    model = artifacts / "linear.joblib"
    dataset = artifacts / "reference.csv"
    destination = alias / "generated.toetra"
    model.write_bytes(b"model")
    dataset.write_text("a,score\n0,1\n", encoding="utf-8")
    monkeypatch.setattr(
        "toetra._runtime.initialization._build_schema",
        lambda **_kwargs: _regression_schema(),
    )

    def validate(specification: Path, **_kwargs: object) -> ValidationResult:
        source = specification.read_text(encoding="utf-8")
        assert 'model := "../artifacts/linear.joblib"' in source
        assert 'dataset := "../artifacts/reference.csv"' in source
        return _valid_result()

    initialize_specification(
        destination,
        model=model,
        target="score",
        dataset=dataset,
        validation_function=validate,
    )

    source = destination.read_text(encoding="utf-8")
    assert 'model := "../artifacts/linear.joblib"' in source
    assert 'dataset := "../artifacts/reference.csv"' in source
