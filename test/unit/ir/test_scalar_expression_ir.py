from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    IntervalDomainIR,
    ScalarValueSource,
    TargetExpressionIR,
    UnaryArithmeticExpressionIR,
)
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.ir1.scalar import format_scalar_expression
from dsl.language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumComparisonOperator,
    EnumUnaryOperator,
)
from dsl.semantic.types.enums import EnumArithmeticClass, EnumDataType


def test_ir1_preserves_symmetric_feature_to_feature_comparison() -> None:
    source = """
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 => x0.a <= x0.b
    """

    comparison = run_ir(source)[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, AttributeExpressionIR)
    assert comparison.left.entity == "x0"
    assert comparison.left.feature == "a"
    assert isinstance(comparison.right, AttributeExpressionIR)
    assert comparison.right.entity == "x0"
    assert comparison.right.feature == "b"


def test_ir1_preserves_nested_affine_arithmetic_and_target_operand() -> None:
    source = """
    model := "model.onnx"
    target := MyTarget

    offset := 3

    [LOGIC]:
    forall x0 => x0.a + 2 * x0.b <= target - offset
    """

    comparison = run_ir(source)[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert comparison.op is EnumComparisonOperator.LTE

    assert isinstance(comparison.left, BinaryArithmeticExpressionIR)
    assert comparison.left.operator is EnumArithmeticOperator.ADD
    assert comparison.left.arithmetic_class is EnumArithmeticClass.AFFINE
    assert isinstance(comparison.left.left, AttributeExpressionIR)

    multiplication = comparison.left.right
    assert isinstance(multiplication, BinaryArithmeticExpressionIR)
    assert multiplication.operator is EnumArithmeticOperator.MUL
    assert multiplication.arithmetic_class is EnumArithmeticClass.AFFINE
    assert isinstance(multiplication.left, ConstantExpressionIR)
    assert multiplication.left.value == 2
    assert isinstance(multiplication.right, AttributeExpressionIR)

    assert isinstance(comparison.right, BinaryArithmeticExpressionIR)
    assert comparison.right.operator is EnumArithmeticOperator.SUB
    assert comparison.right.arithmetic_class is EnumArithmeticClass.AFFINE
    assert isinstance(comparison.right.left, TargetExpressionIR)
    assert comparison.right.left.entity == "_model"
    assert comparison.right.left.feature == "MyTarget"

    offset = comparison.right.right
    assert isinstance(offset, ConstantExpressionIR)
    assert offset.value == 3
    assert offset.dtype is EnumDataType.INT
    assert offset.source_kind is ScalarValueSource.SPECIFICATION_CONSTANT
    assert offset.source_name == "offset"

    assert format_scalar_expression(comparison.left) == "x0.a + 2 * x0.b"
    assert format_scalar_expression(comparison.right) == "_model.MyTarget - 3"


def test_ir1_preserves_unary_expression_and_parenthesized_shape() -> None:
    source = """
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 => -(x0.a + x0.b) <= 0
    """

    comparison = run_ir(source)[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, UnaryArithmeticExpressionIR)
    assert comparison.left.operator is EnumUnaryOperator.MINUS
    assert comparison.left.arithmetic_class is EnumArithmeticClass.AFFINE
    assert isinstance(comparison.left.operand, BinaryArithmeticExpressionIR)
    assert format_scalar_expression(comparison.left) == "-(x0.a + x0.b)"


def test_ir1_preserves_nonlinear_and_symbolic_division_classification() -> None:
    nonlinear_source = """
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 => x0.a * x0.b <= target
    """
    division_source = """
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 => x0.a / x0.b <= target
    """

    nonlinear = run_ir(nonlinear_source)[0].query.expression
    division = run_ir(division_source)[0].query.expression

    assert isinstance(nonlinear, ComparisonIR)
    assert isinstance(nonlinear.left, BinaryArithmeticExpressionIR)
    assert nonlinear.left.arithmetic_class is EnumArithmeticClass.NONLINEAR

    assert isinstance(division, ComparisonIR)
    assert isinstance(division.left, BinaryArithmeticExpressionIR)
    assert division.left.arithmetic_class is EnumArithmeticClass.SYMBOLIC_DIVISION


def test_ir1_preserves_arithmetic_domain_bounds_and_constant_provenance() -> None:
    source = """
    model := "model.onnx"
    target := MyTarget

    margin := 1.5

    [LOGIC]:
    forall x0
        with domain(x0.a: [x0.b - margin, x0.b + margin])
        => x0.a <= 10
    """

    task = run_ir(source)[0]
    assert task.scope.domain is not None
    interval = task.scope.domain.entries[0].constraint

    assert isinstance(interval, IntervalDomainIR)
    assert isinstance(interval.lower, BinaryArithmeticExpressionIR)
    assert isinstance(interval.upper, BinaryArithmeticExpressionIR)

    lower_margin = interval.lower.right
    upper_margin = interval.upper.right
    assert isinstance(lower_margin, ConstantExpressionIR)
    assert isinstance(upper_margin, ConstantExpressionIR)
    assert lower_margin.source_kind is ScalarValueSource.SPECIFICATION_CONSTANT
    assert upper_margin.source_kind is ScalarValueSource.SPECIFICATION_CONSTANT
    assert lower_margin.source_name == "margin"
    assert upper_margin.source_name == "margin"
