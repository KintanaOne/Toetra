from __future__ import annotations

import pytest

from toetra._backends.errors import NoCompatibleBackendError
from toetra._compatibility.defaults import SKLEARN_AFFINE_TO_EXACT_REAL_RULE_ID
from toetra._runtime import verify
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


def _schema(*, coefficient: float = 2.0) -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        metadata={
            "linear": {
                "coef": [coefficient],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )


def test_verify_exposes_the_matched_abstraction_route() -> None:
    session = verify(_SOURCE, schema=_schema())

    assessment = session[0].route.numeric_compatibility
    assert assessment is not None
    assert assessment.matched_rule_id == SKLEARN_AFFINE_TO_EXACT_REAL_RULE_ID
    assert assessment.semantic_target == "toetra.real_affine_extracted_model"
    assert "conclusion scope=semantic_target_only" in session.reports[0].route_reason


def test_verify_rejects_non_finite_model_parameters_before_z3_translation() -> None:
    with pytest.raises(NoCompatibleBackendError, match="NaN or infinity"):
        verify(_SOURCE, schema=_schema(coefficient=float("inf")))


def test_decimal_boundary_proof_is_explicitly_scoped_to_the_real_abstraction() -> None:
    source = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.a: {1.0})
    => target == 0.3
    using Z3
"""
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        metadata={
            "linear": {
                "coef": [0.1],
                "intercept": 0.2,
                "feature_names": ["a"],
            }
        },
    )

    session = verify(source, schema=schema)
    report = session.reports[0]

    assert 0.1 * 1.0 + 0.2 != 0.3
    assert report.status.value == "proved"
    assert report.numeric_compatibility is not None
    assert report.numeric_compatibility.classification == "lossy"
    assert report.numeric_compatibility.conclusion_scope == "semantic_target_only"
    assert "not automatically to concrete source execution" in report.summary
