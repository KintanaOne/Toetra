from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.ast.nodes.primitives import BinaryArithmeticNode, TargetRefNode
from toetra._compiler.builder.program import parse_program
from toetra._compiler.semantic.errors.errors import SemanticError
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from toetra._compiler.semantic.types.enums import EnumArithmeticClass, EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "age": FeatureSchema("age", EnumDataType.INT),
            "income": FeatureSchema("income", EnumDataType.FLOAT),
            "region": FeatureSchema("region", EnumDataType.STRING),
            "active": FeatureSchema("active", EnumDataType.BOOL),
        },
        target="MyTarget",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
    )


def _validate(source: str):
    program = parse_program(parse_toetra_code(source))
    ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=_schema(),
    )
    return program


def test_numeric_affine_expression_is_typed_and_classified() -> None:
    program = _validate("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.age + 2 * x0.income <= target
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    assert isinstance(comparison.left, BinaryArithmeticNode)
    assert comparison.left.semantic is not None
    assert comparison.left.semantic.inferred_dtype is EnumDataType.FLOAT
    assert comparison.left.semantic.arithmetic_class is EnumArithmeticClass.AFFINE
    assert comparison.semantic is not None
    assert comparison.semantic.arithmetic_class is EnumArithmeticClass.AFFINE

    assert isinstance(comparison.right, TargetRefNode)
    assert comparison.right.semantic is not None
    assert comparison.right.semantic.inferred_dtype is EnumDataType.FLOAT


def test_symbolic_product_is_classified_nonlinear() -> None:
    program = _validate("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.age * x0.income <= target
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    assert comparison.left.semantic is not None
    assert comparison.left.semantic.arithmetic_class is EnumArithmeticClass.NONLINEAR


def test_symbolic_denominator_is_classified_symbolic_division() -> None:
    program = _validate("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.age / x0.income <= target
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    assert comparison.left.semantic is not None
    assert (
        comparison.left.semantic.arithmetic_class
        is EnumArithmeticClass.SYMBOLIC_DIVISION
    )


def test_literal_division_by_zero_is_rejected() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.age / (1 - 1) <= target
        """))

    with pytest.raises(SemanticError, match="Literal division by zero"):
        ToetraValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
            model_schema=_schema(),
        )


def test_non_numeric_arithmetic_is_rejected() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.region + 1 <= target
        """))

    with pytest.raises(SemanticError, match="must be numeric, got string"):
        ToetraValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
            model_schema=_schema(),
        )


def test_incompatible_equality_types_are_rejected() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.active == 1
        """))

    with pytest.raises(SemanticError, match="compatible operands"):
        ToetraValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
            model_schema=_schema(),
        )


def test_type_validation_remains_permissive_without_model_schema() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.unknown + 1 <= target
        """))

    assert ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
    )
