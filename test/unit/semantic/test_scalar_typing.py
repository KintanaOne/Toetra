from __future__ import annotations

import pytest

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.ast.nodes.primitives import BinaryArithmeticNode, TargetRefNode
from dsl.builder.program import parse_program
from dsl.parser.errors import ParserError
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.types.enums import EnumArithmeticClass, EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema


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
    program = parse_program(parse_forml_code(source))
    FORMLValidator().validate(
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
    program = parse_program(parse_forml_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.age / (1 - 1) <= target
        """))

    with pytest.raises(ParserError, match="Literal division by zero"):
        FORMLValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
            model_schema=_schema(),
        )


def test_non_numeric_arithmetic_is_rejected() -> None:
    program = parse_program(parse_forml_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.region + 1 <= target
        """))

    with pytest.raises(ParserError, match="must be numeric, got string"):
        FORMLValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
            model_schema=_schema(),
        )


def test_incompatible_equality_types_are_rejected() -> None:
    program = parse_program(parse_forml_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.active == 1
        """))

    with pytest.raises(ParserError, match="compatible operands"):
        FORMLValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
            model_schema=_schema(),
        )


def test_type_validation_remains_permissive_without_model_schema() -> None:
    program = parse_program(parse_forml_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.unknown + 1 <= target
        """))

    assert FORMLValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
    )
