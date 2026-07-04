import pytest

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.types.enums import EnumDataType

from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        task="classification",
        target="MyTarget",
        features={
            "age": FeatureSchema(
                name="age",
                dtype=EnumDataType.INT,
                nullable=False,
            ),
            "income": FeatureSchema(
                name="income",
                dtype=EnumDataType.FLOAT,
                nullable=False,
            ),
            "score": FeatureSchema(
                name="score",
                dtype=EnumDataType.FLOAT,
                nullable=False,
            ),
        },
        metadata={},
    )


def _build(source: str):
    return parse_program(parse_forml_code(source))


def test_schema_aware_validation_accepts_known_feature():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.age <= 30
    """

    ast = _build(source)

    assert FORMLValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
        model_schema=_schema(),
    )


def test_schema_aware_validation_rejects_unknown_feature():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.unknown <= 30
    """

    ast = _build(source)

    with pytest.raises(Exception, match="Unknown feature 'unknown'"):
        FORMLValidator().validate(
            ast,
            tracer=ValidationTracer(enabled=False),
            model_schema=_schema(),
        )


def test_schema_aware_validation_sets_resolved_type_on_attribute():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.income <= 1000
    """

    ast = _build(source)

    FORMLValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
        model_schema=_schema(),
    )

    root = ast.body[0].rule.assertion.root

    assert isinstance(root, ComparisonNode)

    attr = root.left

    assert attr.semantic is not None

    semantic = attr.semantic

    assert semantic.resolved_entity == "x0"
    assert semantic.resolved_path == ["x0", "income"]
    assert semantic.resolved_type == "float"


def test_schema_aware_validation_is_optional_without_model_schema():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.unknown <= 30
    """

    ast = _build(source)

    assert FORMLValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
    )