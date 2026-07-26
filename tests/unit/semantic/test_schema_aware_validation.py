import pytest

from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from toetra._compiler.semantic.types.enums import EnumDataType

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


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
    return parse_program(parse_toetra_code(source))


def test_schema_aware_validation_accepts_known_feature():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall x0 => x0.age <= 30
    """

    ast = _build(source)

    assert ToetraValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
        model_schema=_schema(),
    )


def test_schema_aware_validation_rejects_unknown_feature():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall x0 => x0.unknown <= 30
    """

    ast = _build(source)

    with pytest.raises(Exception, match="Unknown feature 'unknown'"):
        ToetraValidator().validate(
            ast,
            tracer=ValidationTracer(enabled=False),
            model_schema=_schema(),
        )


def test_schema_aware_validation_sets_resolved_type_on_attribute():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall x0 => x0.income <= 1000
    """

    ast = _build(source)

    ToetraValidator().validate(
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
    forall x0 => x0.unknown <= 30
    """

    ast = _build(source)

    assert ToetraValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
    )
