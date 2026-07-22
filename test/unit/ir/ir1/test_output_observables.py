from __future__ import annotations

from dsl.ir.ir1.nodes import AndIR, ComparisonIR, ConstantExpressionIR
from dsl.ir.ir1.outputs import OutputObservableExpressionIR
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import ClassificationOutputSchema, EnumOutputObservable


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={"age": FeatureSchema("age", EnumDataType.INT)},
        output_name="decision",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
        ),
    )


def test_ir1_obs_001_translates_predicted_label_without_model_lowering() -> None:
    task = run_ir(
        """
        model := "model.pkl"
        target := decision

        [LOGIC]:
        forall applicant => target[applicant].label == "approved"
        """,
        model_schema=_schema(),
    )[0]
    comparison = task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, OutputObservableExpressionIR)
    assert comparison.left.observable is EnumOutputObservable.PREDICTED_LABEL
    assert comparison.left.dtype is EnumDataType.STRING
    assert comparison.left.label is None
    assert comparison.left.output_name == "decision"
    assert comparison.left.model_identity == "model.pkl"
    assert comparison.left.point is task.scope.points[0]
    assert isinstance(comparison.right, ConstantExpressionIR)
    assert comparison.right.value == "approved"


def test_ir1_obs_002_preserves_probability_label_intent() -> None:
    task = run_ir(
        """
        model := "model.pkl"
        target := decision

        [LOGIC]:
        forall applicant => target[applicant].probability("approved") >= 0.80
        """,
        model_schema=_schema(),
    )[0]
    comparison = task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, OutputObservableExpressionIR)
    assert comparison.left.observable is EnumOutputObservable.CLASS_PROBABILITY
    assert comparison.left.dtype is EnumDataType.FLOAT
    assert comparison.left.label is not None
    assert comparison.left.label.value == "approved"
    assert comparison.left.label.dtype is EnumDataType.STRING
    assert comparison.left.label.source_lexeme == '"approved"'


def test_ir1_obs_003_reuses_one_evaluation_for_multiple_observables() -> None:
    task = run_ir(
        """
        model := "model.pkl"
        target := decision

        [LOGIC]:
        forall applicant =>
            target[applicant].label == "approved"
            and target[applicant].probability("approved") >= 0.80
        """,
        model_schema=_schema(),
    )[0]
    expression = task.query.expression
    assert isinstance(expression, AndIR)
    left, right = expression.operands
    assert isinstance(left, ComparisonIR)
    assert isinstance(right, ComparisonIR)
    assert isinstance(left.left, OutputObservableExpressionIR)
    assert isinstance(right.left, OutputObservableExpressionIR)
    assert left.left.evaluation is right.left.evaluation


def test_ir1_obs_004_distinct_points_produce_distinct_evaluations() -> None:
    task = run_ir(
        """
        model := "model.pkl"
        target := decision

        [LOGIC]:
        forall left, right =>
            target[left].label == target[right].label
        """,
        model_schema=_schema(),
    )[0]
    comparison = task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, OutputObservableExpressionIR)
    assert isinstance(comparison.right, OutputObservableExpressionIR)
    assert comparison.left.evaluation is not comparison.right.evaluation
    assert comparison.left.point.name == "left"
    assert comparison.right.point.name == "right"


def test_ir1_obs_005_different_probability_labels_share_evaluation_only() -> None:
    task = run_ir(
        """
        model := "model.pkl"
        target := decision

        [LOGIC]:
        forall applicant =>
            target[applicant].probability("approved") >= 0.80
            and target[applicant].probability("rejected") <= 0.20
        """,
        model_schema=_schema(),
    )[0]
    expression = task.query.expression
    assert isinstance(expression, AndIR)
    left, right = expression.operands
    assert isinstance(left, ComparisonIR)
    assert isinstance(right, ComparisonIR)
    assert isinstance(left.left, OutputObservableExpressionIR)
    assert isinstance(right.left, OutputObservableExpressionIR)
    assert left.left.evaluation is right.left.evaluation
    assert left.left.label is not None
    assert right.left.label is not None
    assert left.left.label.value == "approved"
    assert right.left.label.value == "rejected"
    assert left.left != right.left
