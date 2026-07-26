from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.ast.nodes.primitives import (
    AttributeNode,
    BinaryArithmeticNode,
    ConstantNode,
    TargetRefNode,
)
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer


def _build_and_validate(source: str):
    program = parse_program(parse_toetra_code(source))
    ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
    )
    return program


def test_bare_name_resolves_to_constant_before_implicit_feature() -> None:
    program = _build_and_validate("""
        model := "model.onnx"
        target := MyTarget

        threshold := 7

        [LOGIC]:
        forall x0 => x0.score <= threshold
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    right = comparison.right

    assert isinstance(right, ConstantNode)
    assert right.value == 7
    assert right.semantic is not None
    assert right.semantic.resolved_symbol is not None
    assert right.semantic.resolved_symbol.name == "threshold"


def test_absent_constant_falls_back_to_implicit_feature() -> None:
    program = _build_and_validate("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall applicant => income >= 25000
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    left = comparison.left

    assert isinstance(left, AttributeNode)
    assert left.entity is None
    assert left.feature == "income"
    assert left.semantic is not None
    assert left.semantic.resolved_entity == "applicant"
    assert left.semantic.resolved_path == ["applicant", "income"]


def test_explicit_feature_is_not_shadowed_by_constant_name() -> None:
    program = _build_and_validate("""
        model := "model.onnx"
        target := MyTarget

        threshold := 7

        [LOGIC]:
        forall x0 => x0.threshold <= threshold
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)

    assert isinstance(comparison.left, AttributeNode)
    assert comparison.left.feature == "threshold"
    assert comparison.left.semantic is not None
    assert comparison.left.semantic.resolved_entity == "x0"

    assert isinstance(comparison.right, ConstantNode)
    assert comparison.right.value == 7


def test_target_reference_is_bound_on_right_side_too() -> None:
    program = _build_and_validate("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.score <= target
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    right = comparison.right

    assert isinstance(right, TargetRefNode)
    assert right.semantic is not None
    assert right.semantic.resolved_entity == "_model"
    assert right.semantic.resolved_path == ["_model", "MyTarget"]


def test_binding_recurses_through_arithmetic_tree() -> None:
    program = _build_and_validate("""
        model := "model.onnx"
        target := MyTarget

        weight := 2

        [LOGIC]:
        forall x0 => x0.a + weight * x0.b <= target
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    expression = comparison.left

    assert isinstance(expression, BinaryArithmeticNode)
    assert isinstance(expression.left, AttributeNode)
    assert expression.left.semantic is not None
    assert expression.left.semantic.resolved_entity == "x0"

    product = expression.right
    assert isinstance(product, BinaryArithmeticNode)
    assert isinstance(product.left, ConstantNode)
    assert product.left.value == 2
    assert product.left.semantic is not None
    assert product.left.semantic.resolved_symbol is not None
    assert product.left.semantic.resolved_symbol.name == "weight"

    assert isinstance(product.right, AttributeNode)
    assert product.right.semantic is not None
    assert product.right.semantic.resolved_entity == "x0"


def test_unknown_explicit_entity_is_not_aliased_to_only_scope_variable() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => y.age >= 18
        """))

    with pytest.raises(ParserError, match="Unknown variable 'y'"):
        ToetraValidator().validate(program, tracer=ValidationTracer(enabled=False))
