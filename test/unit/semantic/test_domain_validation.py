from __future__ import annotations

import pytest

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.errors import ParserError
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


def _assert_rejected(source: str, message: str) -> None:
    program = parse_program(parse_toetra_code(source))
    with pytest.raises(ParserError, match=message):
        ToetraValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
            model_schema=_schema(),
        )


def test_duplicate_domain_subject_is_rejected() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(
            x0.age: [0, 10],
            x0.age: [2, 8]
        ) => target <= 1
        """,
        "Duplicate domain subject",
    )


def test_implicit_domain_subject_is_rejected() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(age: [0, 10]) => target <= 1
        """,
        "must be explicitly qualified",
    )


def test_reversed_constant_interval_is_rejected() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.age: [5, 3]) => target <= 1
        """,
        "Reversed interval",
    )


@pytest.mark.parametrize(
    "interval",
    ["]3, 3]", "[3, 3[", "]3, 3["],
)
def test_open_equal_constant_interval_is_rejected(interval: str) -> None:
    _assert_rejected(
        f"""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.age: {interval}) => target <= 1
        """,
        "Empty interval",
    )


def test_closed_singleton_interval_is_valid() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.age: [3, 3]) => target <= 1
        """))

    assert ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=_schema(),
    )


def test_target_in_domain_bound_is_rejected() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.age: [0, target]) => target <= 1
        """,
        "Model target cannot be used in domain bounds",
    )


def test_non_numeric_interval_bound_is_rejected() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := MyTarget

        region_floor := "EU"

        [LOGIC]:
        forall x0 with domain(x0.age: [region_floor, 10]) => target <= 1
        """,
        "lower bound must be numeric",
    )


def test_numeric_subject_rejects_symbolic_finite_set_members() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.age: {EU, US}) => target <= 1
        """,
        "incompatible with subject",
    )


def test_string_subject_accepts_symbolic_and_string_members() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        preferred := "EU"

        [LOGIC]:
        forall x0 with domain(x0.region: {preferred, US}) => target <= 1
        """))

    assert ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=_schema(),
    )


def test_domain_arithmetic_division_by_zero_is_rejected() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.age: [0, 10 / (2 - 2)]) => target <= 1
        """,
        "Literal division by zero",
    )
