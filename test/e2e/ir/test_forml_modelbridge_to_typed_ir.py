from dsl.builder.program import parse_program
from dsl.ir.ir1.nodes import ComparisonIR
from dsl.ir.ir1.translator import IRTranslator
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.types.enums import EnumDataType
from model.runtime.manager import ModelManager
from test.fixtures.ir_schema_aware.e2e_factories import create_tiny_sklearn_artifacts


def test_forml_modelbridge_schema_validation_to_typed_ir(tmp_path):
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
    check_at x0 => x0.income <= 1000
    """

    ast = parse_program(parse_forml_code(source))

    FORMLValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
        model_schema=schema,
    )

    tasks = IRTranslator().translate(ast)
    comparison = tasks[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert comparison.entity == "x0"
    assert comparison.feature == "income"
    assert comparison.feature_dtype is EnumDataType.FLOAT
    assert comparison.value_dtype is EnumDataType.INT


def test_forml_modelbridge_rejects_unknown_feature_before_ir(tmp_path):
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
    check_at x0 => x0.unknown <= 1000
    """

    ast = parse_program(parse_forml_code(source))

    try:
        FORMLValidator().validate(
            ast,
            tracer=ValidationTracer(enabled=False),
            model_schema=schema,
        )
    except Exception as exc:
        assert "Unknown feature 'unknown'" in str(exc)
    else:
        raise AssertionError("Expected unknown feature validation to fail")
