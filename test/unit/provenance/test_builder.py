from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._provenance import builder as provenance_builder
from toetra._provenance.builder import build_provenance_context
from toetra._provenance.model import FingerprintStatus, ProvenanceCompleteness
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    BinaryClassificationDecisionPolicy,
    ClassificationOutputSchema,
)


def _schema(*, coefficient: float = 2.0) -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "a": FeatureSchema(
                name="a", dtype=EnumDataType.FLOAT, source_dtype="float64"
            )
        },
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        target_source_dtype="float64",
        metadata={
            "linear": {
                "coef": [coefficient],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )


def _context(**overrides: object):
    arguments = {
        "specification_source": "target <= 7",
        "specification_path": None,
        "model_path": None,
        "dataset_path": None,
        "anchor_source": None,
        "anchor_resolver": None,
        "anchors_used": False,
        "schema": _schema(),
        "ir2_context": IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
        "captured_at": datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    }
    arguments.update(overrides)
    return build_provenance_context(**arguments)  # type: ignore[arg-type]


def test_software_provenance_uses_toetra_distribution_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requested: list[str] = []

    def version(name: str) -> str:
        requested.append(name)
        return f"version:{name}"

    monkeypatch.setattr(
        provenance_builder.importlib.metadata,
        "version",
        version,
    )

    context = _context()

    assert context.software.toetra_version == "version:toetra"
    assert "toetra" in requested
    assert "forml" not in requested


def test_schema_only_provenance_is_complete() -> None:
    context = _context()
    assert context.completeness is ProvenanceCompleteness.COMPLETE
    assert context.artifacts["model"].status is FingerprintStatus.NOT_PROVIDED
    assert context.artifacts["model_schema"].status is FingerprintStatus.AVAILABLE


def test_file_fingerprints_use_exact_bytes_and_ignore_names(tmp_path: Path) -> None:
    left = tmp_path / "model-a.joblib"
    right = tmp_path / "renamed.joblib"
    left.write_bytes(b"same-model")
    right.write_bytes(b"same-model")

    first = _context(model_path=left)
    second = _context(model_path=right)

    assert first.artifacts["model"].fingerprint == second.artifacts["model"].fingerprint
    assert first.input_fingerprint == second.input_fingerprint


def test_dataframe_anchor_source_has_canonical_fingerprint() -> None:
    frame = pd.DataFrame({"id": ["a"], "x": [1.0]})
    context = _context(anchor_source=frame, anchors_used=True)
    artifact = context.artifacts["anchor_source"]
    assert artifact.status is FingerprintStatus.AVAILABLE
    assert artifact.fingerprint is not None
    assert artifact.fingerprint.canonicalization == "pandas_dataframe_canonical_json_v1"


def test_opaque_anchor_resolver_marks_provenance_partial() -> None:
    context = _context(anchor_resolver=object(), anchors_used=True)
    assert context.completeness is ProvenanceCompleteness.PARTIAL
    assert context.unavailable_inputs == ("anchor_source",)


def test_schema_change_changes_input_identity() -> None:
    first = _context(schema=_schema(coefficient=2.0))
    second = _context(schema=_schema(coefficient=3.0))
    assert first.input_fingerprint != second.input_fingerprint


def test_software_provenance_uses_toetra_build_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TOETRA_BUILD_ID", "build:toetra-test")
    monkeypatch.setenv("FORML_BUILD_ID", "legacy-build-id")

    context = _context()

    assert context.software.toetra_build_id == "build:toetra-test"


def test_typed_output_schema_changes_model_schema_fingerprint() -> None:
    base = {
        "framework": EnumModelFramework.SKLEARN,
        "model_type": "Classifier",
        "features": {
            "a": FeatureSchema(
                name="a", dtype=EnumDataType.FLOAT, source_dtype="float64"
            )
        },
        "output_name": "decision",
        "task": "classification",
        "metadata": {},
    }
    without_probability = ModelSchema(
        **base,
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=False,
        ),
    )
    with_probability = ModelSchema(
        **base,
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
        ),
    )

    first = _context(schema=without_probability)
    second = _context(schema=with_probability)

    first_schema = first.artifacts["model_schema"].fingerprint
    second_schema = second.artifacts["model_schema"].fingerprint
    assert first_schema is not None
    assert second_schema is not None
    assert first_schema.canonicalization == "toetra_model_schema_canonical_json_v3"
    assert second_schema.canonicalization == "toetra_model_schema_canonical_json_v3"
    assert first_schema != second_schema


def test_binary_decision_policy_changes_model_schema_fingerprint() -> None:
    base = {
        "framework": EnumModelFramework.SKLEARN,
        "model_type": "LogisticRegression",
        "features": {
            "a": FeatureSchema(
                name="a", dtype=EnumDataType.FLOAT, source_dtype="float64"
            )
        },
        "output_name": "decision",
        "task": "classification",
        "metadata": {},
    }
    native = ModelSchema(
        **base,
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
            decision_policy=BinaryClassificationDecisionPolicy(
                negative_label="rejected",
                positive_label="approved",
            ),
        ),
    )
    changed_threshold = ModelSchema(
        **base,
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
            decision_policy=BinaryClassificationDecisionPolicy(
                negative_label="rejected",
                positive_label="approved",
                probability_threshold="0.6",
            ),
        ),
    )

    first = _context(schema=native).artifacts["model_schema"].fingerprint
    second = _context(schema=changed_threshold).artifacts["model_schema"].fingerprint

    assert first is not None
    assert second is not None
    assert first.canonicalization == "toetra_model_schema_canonical_json_v3"
    assert second.canonicalization == "toetra_model_schema_canonical_json_v3"
    assert first != second
