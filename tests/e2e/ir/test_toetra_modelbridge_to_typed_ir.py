from toetra._compiler.builder.program import parse_program
from toetra._compiler.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
)
from toetra._compiler.ir.ir1.translator import IRTranslator
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.runtime.manager import ModelManager
from tests.support.ir_schema_artifacts import create_tiny_sklearn_artifacts


def test_toetra_modelbridge_schema_validation_to_typed_ir(tmp_path):
    model_path, dataset_path = create_tiny_sklearn_artifacts(tmp_path)

    schema = ModelManager(
        model_path=model_path,
        dataset_path=dataset_path,
        target_name="MyTarget",
    ).build_schema()

    source = f"""
    model := "{model_path.as_posix()}"
    target := MyTarget

    [ROBUSTNESS]:
    forall x0 => x0.income <= 1000
    """

    ast = parse_program(parse_toetra_code(source))

    ToetraValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
        model_schema=schema,
    )

    tasks = IRTranslator().translate(ast)
    comparison = tasks[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, AttributeExpressionIR)
    assert comparison.left.entity == "x0"
    assert comparison.left.feature == "income"
    assert comparison.left.dtype is EnumDataType.FLOAT

    assert isinstance(comparison.right, ConstantExpressionIR)
    assert comparison.right.dtype is EnumDataType.INT


def test_toetra_modelbridge_rejects_unknown_feature_before_ir(tmp_path):
    model_path, dataset_path = create_tiny_sklearn_artifacts(tmp_path)

    schema = ModelManager(
        model_path=model_path,
        dataset_path=dataset_path,
        target_name="MyTarget",
    ).build_schema()

    source = f"""
    model := "{model_path.as_posix()}"
    target := MyTarget

    [ROBUSTNESS]:
    forall x0 => x0.unknown <= 1000
    """

    ast = parse_program(parse_toetra_code(source))

    try:
        ToetraValidator().validate(
            ast,
            tracer=ValidationTracer(enabled=False),
            model_schema=schema,
        )
    except Exception as exc:
        assert "Unknown feature 'unknown'" in str(exc)
    else:
        raise AssertionError("Expected unknown feature validation to fail")
