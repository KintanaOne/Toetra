from __future__ import annotations

from dsl.ir.ir1.nodes import ComparisonIR, NotIR, OrIR
from dsl.ir.ir1.outputs import OutputObservableExpressionIR
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.normalization.nnf import NNFNormalizer
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import ClassificationOutputSchema


def test_nnf_preserves_output_observable_and_shared_evaluation_identity() -> None:
    schema = ModelSchema(
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
    task = run_ir(
        """
        model := "model.pkl"
        target := decision

        [LOGIC]:
        forall x => not (
            target[x].label == "approved"
            and target[x].probability("approved") >= 0.80
        )
        """,
        model_schema=schema,
    )[0]
    normalized = NNFNormalizer().normalize_expr(task.query.expression)
    assert isinstance(normalized, OrIR)
    comparisons: list[ComparisonIR] = []
    for item in normalized.operands:
        assert isinstance(item, NotIR)
        assert isinstance(item.operand, ComparisonIR)
        comparisons.append(item.operand)
    left = comparisons[0].left
    right = comparisons[1].left
    assert isinstance(left, OutputObservableExpressionIR)
    assert isinstance(right, OutputObservableExpressionIR)
    assert left.evaluation is right.evaluation
