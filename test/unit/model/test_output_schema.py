import pytest

from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.schema.output_schema import (
    BinaryClassificationDecisionPolicy,
    ClassificationOutputSchema,
    EnumModelOutputKind,
    EnumOutputObservable,
    RegressionOutputSchema,
    UnknownOutputSchema,
)


def test_regression_output_schema_exposes_one_scalar_value() -> None:
    schema = RegressionOutputSchema(
        value_dtype=EnumDataType.FLOAT,
        value_source_dtype="float64",
    )

    assert schema.kind is EnumModelOutputKind.REGRESSION
    assert schema.primary_dtype is EnumDataType.FLOAT
    assert schema.source_dtype == "float64"
    assert schema.available_observables == (EnumOutputObservable.REGRESSION_VALUE,)


def test_classification_output_schema_exposes_ordered_labels_and_probability() -> None:
    schema = ClassificationOutputSchema(
        label_dtype=EnumDataType.STRING,
        labels=("rejected", "approved"),
        label_source_dtype="object",
        probability_available=True,
    )

    assert schema.kind is EnumModelOutputKind.CLASSIFICATION
    assert schema.primary_dtype is EnumDataType.STRING
    assert schema.source_dtype == "object"
    assert schema.labels == ("rejected", "approved")
    assert schema.available_observables == (
        EnumOutputObservable.PREDICTED_LABEL,
        EnumOutputObservable.CLASS_PROBABILITY,
    )


def test_classification_output_schema_omits_probability_when_unavailable() -> None:
    schema = ClassificationOutputSchema(
        label_dtype=EnumDataType.INT,
        labels=(0, 1),
    )

    assert schema.available_observables == (EnumOutputObservable.PREDICTED_LABEL,)


def test_classification_output_schema_rejects_duplicate_labels() -> None:
    with pytest.raises(ValueError, match="labels must be unique"):
        ClassificationOutputSchema(labels=("approved", "approved"))


def test_classification_output_schema_rejects_non_serializable_labels() -> None:
    with pytest.raises(TypeError, match="JSON-compatible scalar"):
        ClassificationOutputSchema(labels=(object(),))  # type: ignore[arg-type]


def test_classification_output_schema_rejects_non_finite_labels() -> None:
    with pytest.raises(ValueError, match="labels must be finite"):
        ClassificationOutputSchema(labels=(float("nan"),))


def test_unknown_output_schema_exposes_no_public_observable() -> None:
    schema = UnknownOutputSchema(value_dtype=EnumDataType.FLOAT)

    assert schema.kind is EnumModelOutputKind.UNKNOWN
    assert schema.available_observables == ()
    assert schema.primary_dtype is EnumDataType.FLOAT


def test_binary_decision_policy_preserves_native_threshold_provenance() -> None:
    policy = BinaryClassificationDecisionPolicy(
        negative_label="rejected",
        positive_label="approved",
    )
    schema = ClassificationOutputSchema(
        label_dtype=EnumDataType.STRING,
        labels=("rejected", "approved"),
        probability_available=True,
        decision_policy=policy,
    )

    assert policy.probability_threshold == "0.5"
    assert policy.oriented_decision_threshold == "0"
    assert policy.positive_when_strictly_greater is True
    assert policy.equality_label == "rejected"
    assert policy.policy_source == "recognized_model_profile"
    assert schema.decision_policy is policy


def test_binary_decision_policy_requires_matching_label_orientation() -> None:
    policy = BinaryClassificationDecisionPolicy(
        negative_label="rejected",
        positive_label="approved",
    )

    with pytest.raises(ValueError, match="negative/positive orientation"):
        ClassificationOutputSchema(
            labels=("approved", "rejected"),
            probability_available=True,
            decision_policy=policy,
        )
