from __future__ import annotations

import json

from dsl.runtime import verify
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


def test_verify_exposes_stable_property_provenance() -> None:
    first = verify(_SOURCE, schema=_schema())
    second = verify(_SOURCE, schema=_schema())
    report = first.reports[0]

    assert first.provenance is not None
    assert report.provenance is not None
    assert report.provenance.input_fingerprint == first.provenance.input_fingerprint
    assert (
        report.provenance.verification_fingerprint
        == second.reports[0].provenance.verification_fingerprint  # type: ignore[union-attr]
    )
    assert report.provenance.captured_at_utc != ""


def test_provenance_is_exported_to_all_report_surfaces() -> None:
    session = verify(_SOURCE, schema=_schema())
    payload = json.loads(session.to_json())
    report_payload = payload["reports"][0]

    assert payload["schema_version"] == 5
    assert set(payload["provenance"]["fingerprints"]) == {"inputs"}
    assert "verification" in report_payload["provenance"]["fingerprints"]
    assert "Verification provenance" in session.to_text()
    assert "Verification provenance" in session.to_html()
    assert session.to_records()[0]["verification_fingerprint"].startswith("sha256:")
