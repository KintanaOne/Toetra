from __future__ import annotations

import pandas as pd
from sklearn.linear_model import LogisticRegression

from toetra._models.introspector.sklearn_introspector import SklearnIntrospector
from toetra._models.schema.output_schema import (
    BinaryClassificationDecisionPolicy,
    ClassificationOutputSchema,
)
from toetra._models.families import BINARY_LOGISTIC_AFFINE_MODEL_FAMILY


def _binary_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "income": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
            "debt": [50.0, 40.0, 35.0, 20.0, 10.0, 5.0],
            "decision": [0, 0, 0, 1, 1, 1],
        }
    )


def test_direct_fitted_binary_logistic_regression_gets_frozen_profile(tmp_path) -> None:
    frame = _binary_frame()
    model = LogisticRegression(random_state=0).fit(
        frame[["income", "debt"]], frame["decision"]
    )
    dataset = tmp_path / "binary.csv"
    frame.to_csv(dataset, index=False)

    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="decision",
    ).introspect()

    assert schema.compatibility is not None
    assert schema.compatibility.model_family == BINARY_LOGISTIC_AFFINE_MODEL_FAMILY
    assert isinstance(schema.output_schema, ClassificationOutputSchema)
    assert schema.output_schema.decision_policy == BinaryClassificationDecisionPolicy(
        negative_label=0,
        positive_label=1,
    )
    assert schema.metadata["linear"]["feature_names"] == ["income", "debt"]
    assert len(schema.metadata["linear"]["coef"]) == 1
    assert len(schema.metadata["linear"]["intercept"]) == 1


def test_unfitted_logistic_regression_is_not_classified_as_supported_profile(
    tmp_path,
) -> None:
    frame = _binary_frame()
    dataset = tmp_path / "binary.csv"
    frame.to_csv(dataset, index=False)

    schema = SklearnIntrospector(
        model=LogisticRegression(),
        source_path=dataset,
        target_name="decision",
    ).introspect()

    assert schema.compatibility is not None
    assert schema.compatibility.model_family.startswith("unknown:")
    assert isinstance(schema.output_schema, ClassificationOutputSchema)
    assert schema.output_schema.decision_policy is None
    assert "linear" not in schema.metadata


def test_multiclass_logistic_regression_is_not_classified_as_binary_profile(
    tmp_path,
) -> None:
    frame = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            "b": [1.0, 0.0, 1.0, 0.0, 1.0, 0.0],
            "decision": [0, 0, 1, 1, 2, 2],
        }
    )
    model = LogisticRegression(random_state=0).fit(frame[["a", "b"]], frame["decision"])
    dataset = tmp_path / "multiclass.csv"
    frame.to_csv(dataset, index=False)

    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="decision",
    ).introspect()

    assert schema.compatibility is not None
    assert schema.compatibility.model_family.startswith("unknown:")
    assert isinstance(schema.output_schema, ClassificationOutputSchema)
    assert schema.output_schema.decision_policy is None
