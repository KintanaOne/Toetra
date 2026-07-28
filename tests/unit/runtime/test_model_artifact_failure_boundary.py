from __future__ import annotations

from pathlib import Path

import pytest

import toetra._runtime.api as runtime_api
from toetra import (
    VerificationConfigurationError,
    VerificationRuntimeError,
    verify,
)
from toetra._models.errors.base import ModelError
from toetra._models.errors.detection import (
    ModelDetectionError,
    UnsupportedModelError,
)
from toetra._models.errors.introspection import (
    MissingFeatureMetadataError,
    ModelIntrospectionError,
    ReferenceDatasetError,
    UnsupportedIntrospectorError,
)
from toetra._models.errors.loading import (
    ModelDeserializationError,
    ModelLoadingError,
    UnsupportedModelFormatError,
)

_SOURCE = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0 => x0.a <= 7.0
"""


def test_verify_reports_missing_model_artifact(tmp_path: Path) -> None:
    model_path = tmp_path / "missing.joblib"

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(_SOURCE, model=model_path)

    error = caught.value
    assert error.code == "MODEL_ARTIFACT_NOT_FOUND"
    assert error.stage == "model"
    assert error.path == str(model_path)
    assert error.hint is not None


def test_verify_reports_missing_reference_dataset(tmp_path: Path) -> None:
    model_path = tmp_path / "model.joblib"
    dataset_path = tmp_path / "missing.csv"
    model_path.write_bytes(b"placeholder")

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(_SOURCE, model=model_path, dataset=dataset_path)

    error = caught.value
    assert error.code == "MODEL_DATASET_NOT_FOUND"
    assert error.stage == "model"
    assert error.path == str(dataset_path)
    assert error.hint is not None


def test_verify_reports_unsupported_model_artifact_format(tmp_path: Path) -> None:
    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(b"placeholder")

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(_SOURCE, model=model_path)

    error = caught.value
    assert error.code == "MODEL_ARTIFACT_FORMAT_UNSUPPORTED"
    assert error.stage == "model"
    assert error.path == str(model_path)
    assert isinstance(error.__cause__, UnsupportedModelFormatError)


def test_verify_reports_model_deserialization_failure(tmp_path: Path) -> None:
    model_path = tmp_path / "model.joblib"
    model_path.write_bytes(b"not a joblib artifact")

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(_SOURCE, model=model_path)

    error = caught.value
    assert error.code == "MODEL_ARTIFACT_DESERIALIZATION_FAILED"
    assert error.stage == "model"
    assert error.path == str(model_path)
    assert isinstance(error.__cause__, ModelDeserializationError)


def test_verify_reports_loaded_but_unsupported_model(tmp_path: Path) -> None:
    model_path = tmp_path / "model.json"
    model_path.write_text('{"kind": "not-a-model"}', encoding="utf-8")

    with pytest.raises(VerificationRuntimeError) as caught:
        verify(_SOURCE, model=model_path)

    error = caught.value
    assert not isinstance(error, VerificationConfigurationError)
    assert error.code == "MODEL_TYPE_UNSUPPORTED"
    assert error.stage == "model"
    assert error.path == str(model_path)
    assert isinstance(error.__cause__, UnsupportedModelError)


@pytest.mark.parametrize(
    ("private_error", "public_type", "code", "path_owner"),
    [
        (
            UnsupportedModelFormatError("unsupported format"),
            VerificationConfigurationError,
            "MODEL_ARTIFACT_FORMAT_UNSUPPORTED",
            "model",
        ),
        (
            ModelDeserializationError("invalid serialization"),
            VerificationConfigurationError,
            "MODEL_ARTIFACT_DESERIALIZATION_FAILED",
            "model",
        ),
        (
            ModelLoadingError("invalid artifact"),
            VerificationConfigurationError,
            "MODEL_ARTIFACT_INVALID",
            "model",
        ),
        (
            ReferenceDatasetError("invalid dataset"),
            VerificationConfigurationError,
            "MODEL_DATASET_READ_FAILED",
            "dataset",
        ),
        (
            MissingFeatureMetadataError("metadata required"),
            VerificationConfigurationError,
            "MODEL_FEATURE_METADATA_REQUIRED",
            "dataset",
        ),
        (
            UnsupportedModelError("unsupported model"),
            VerificationRuntimeError,
            "MODEL_TYPE_UNSUPPORTED",
            "model",
        ),
        (
            UnsupportedIntrospectorError("unsupported framework"),
            VerificationRuntimeError,
            "MODEL_FRAMEWORK_UNSUPPORTED",
            "model",
        ),
        (
            ModelDetectionError("detection failed"),
            VerificationRuntimeError,
            "MODEL_DETECTION_FAILED",
            "model",
        ),
        (
            ModelIntrospectionError("introspection failed"),
            VerificationRuntimeError,
            "MODEL_INTROSPECTION_FAILED",
            "dataset",
        ),
        (
            ModelError("processing failed"),
            VerificationRuntimeError,
            "MODEL_PROCESSING_FAILED",
            "model",
        ),
    ],
)
def test_verify_normalizes_private_model_failures(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    private_error: ModelError,
    public_type: type[VerificationRuntimeError],
    code: str,
    path_owner: str,
) -> None:
    model_path = tmp_path / "model.joblib"
    dataset_path = tmp_path / "dataset.csv"
    model_path.write_bytes(b"placeholder")
    dataset_path.write_text("a,score\n1.0,2.0\n", encoding="utf-8")

    def reject_model(_manager: object) -> None:
        raise private_error

    monkeypatch.setattr(runtime_api.ModelManager, "build_schema", reject_model)

    with pytest.raises(public_type) as caught:
        verify(_SOURCE, model=model_path, dataset=dataset_path)

    error = caught.value
    expected_path = model_path if path_owner == "model" else dataset_path
    assert error.code == code
    assert error.stage == "model"
    assert error.path == str(expected_path)
    assert error.hint is not None
    assert error.__cause__ is private_error
