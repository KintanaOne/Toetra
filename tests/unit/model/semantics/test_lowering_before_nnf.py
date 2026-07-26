from __future__ import annotations

from toetra._compiler.ir.ir1.model_quantities import ModelQuantityExpressionIR
from toetra._compiler.ir.ir1.nodes import ComparisonIR, NotIR, OrIR
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._compiler.ir.normalization.nnf import NNFNormalizer
from toetra._models.semantics.lowering import ModelSemanticLowerer
from tests.support.model_semantics import make_binary_logistic_schema


def test_model_semantic_lowering_occurs_before_nnf() -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(
        """
        model := "credit.joblib"
        target := decision
        [LOGIC]:
        forall applicant =>
            target[applicant].label == "approved"
            -> target[applicant].label != "rejected"
        """,
        model_schema=schema,
    )[0]

    lowered = ModelSemanticLowerer().lower_task(task, schema=schema)
    normalized = NNFNormalizer().normalize_task(lowered.task)

    expression = normalized.query.expression
    assert isinstance(expression, OrIR)
    assert isinstance(expression.operands[0], NotIR)
    negated = expression.operands[0].operand
    assert isinstance(negated, ComparisonIR)
    assert isinstance(negated.left, ModelQuantityExpressionIR)
    positive = expression.operands[1]
    assert isinstance(positive, ComparisonIR)
    assert isinstance(positive.left, ModelQuantityExpressionIR)
