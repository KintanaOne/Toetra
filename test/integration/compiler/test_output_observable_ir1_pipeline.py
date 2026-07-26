from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import AndIR, ComparisonIR
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._compiler.ir.ir1.pretty import pretty_task
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    EnumOutputObservable,
)


def test_source_to_ir1_preserves_declarative_classification_observables() -> None:
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={"income": FeatureSchema("income", EnumDataType.FLOAT)},
        output_name="decision",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
        ),
    )
    task = run_ir(
        """
        model := "credit.joblib"
        target := decision

        [LOGIC]:
        forall applicant =>
            target[applicant].label == "approved"
            and target[applicant].probability("approved") >= 0.80
        """,
        model_schema=schema,
    )[0]
    expression = task.query.expression
    assert isinstance(expression, AndIR)
    label_comparison, probability_comparison = expression.operands
    assert isinstance(label_comparison, ComparisonIR)
    assert isinstance(probability_comparison, ComparisonIR)
    assert isinstance(label_comparison.left, OutputObservableExpressionIR)
    assert isinstance(probability_comparison.left, OutputObservableExpressionIR)
    assert label_comparison.left.observable is EnumOutputObservable.PREDICTED_LABEL
    assert (
        probability_comparison.left.observable is EnumOutputObservable.CLASS_PROBABILITY
    )
    assert label_comparison.left.evaluation is probability_comparison.left.evaluation
    rendered = pretty_task(task)
    assert "target[applicant].label : string == 'approved'" in rendered
    assert "target[applicant].probability('approved') : float >= 0.8" in rendered
