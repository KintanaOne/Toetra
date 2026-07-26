from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import ComparisonIR, NotIR, OrIR
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._compiler.ir.normalization.nnf import NNFNormalizer
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import ClassificationOutputSchema


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
