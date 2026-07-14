from __future__ import annotations

from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ScalarValueSource,
    TargetExpressionIR,
)
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.semantic.types.enums import EnumDataType


def test_specification_constant_reaches_ir1_with_provenance() -> None:
    source = """
    model := "model.onnx"
    target := MyTarget

    maximum_age := 65

    [LOGIC]:
    forall applicant => applicant.age <= maximum_age
    """

    comparison = run_ir(source)[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, AttributeExpressionIR)
    assert comparison.left.entity == "applicant"
    assert comparison.left.feature == "age"

    assert isinstance(comparison.right, ConstantExpressionIR)
    assert comparison.right.value == 65
    assert comparison.right.dtype is EnumDataType.INT
    assert comparison.right.source_kind is ScalarValueSource.SPECIFICATION_CONSTANT
    assert comparison.right.source_name == "maximum_age"


def test_target_can_be_compared_to_specification_constant() -> None:
    source = """
    model := "model.onnx"
    target := MyTarget

    max_risk := 0.2

    [BOUND]:
    forall applicant => target <= max_risk
    """

    comparison = run_ir(source)[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, TargetExpressionIR)
    assert comparison.left.entity == "_model"
    assert comparison.left.feature == "MyTarget"

    assert isinstance(comparison.right, ConstantExpressionIR)
    assert comparison.right.value == 0.2
    assert comparison.right.dtype is EnumDataType.FLOAT
    assert comparison.right.source_kind is ScalarValueSource.SPECIFICATION_CONSTANT
    assert comparison.right.source_name == "max_risk"
