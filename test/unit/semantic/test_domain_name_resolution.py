from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.domain import (
    FiniteSetDomainNode,
    IntervalDomainNode,
    SymbolLiteralNode,
)
from toetra._compiler.ast.nodes.expressions import QuantifierExprNode
from toetra._compiler.ast.nodes.primitives import (
    AttributeNode,
    BinaryArithmeticNode,
    ConstantNode,
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


def test_domain_bound_resolves_matching_specification_constant() -> None:
    program = _build_and_validate("""
        model := "model.onnx"
        target := MyTarget

        minimum_income := 25000

        [LOGIC]:
        forall applicant
            with domain(applicant.income: [minimum_income, 100000])
            => target <= 1
        """)

    scope = program.body[0].rule.scope
    assert isinstance(scope, QuantifierExprNode)
    domain = scope.domain
    assert domain is not None

    interval = domain.entries[0].constraint
    assert isinstance(interval, IntervalDomainNode)
    assert isinstance(interval.lower, ConstantNode)
    assert interval.lower.value == 25000
    assert interval.lower.semantic is not None
    assert interval.lower.semantic.resolved_symbol is not None
    assert interval.lower.semantic.resolved_symbol.name == "minimum_income"


def test_unknown_bare_domain_bound_is_rejected() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall applicant
            with domain(applicant.income: [minimum_income, 100000])
            => target <= 1
        """))

    with pytest.raises(
        ParserError,
        match="Unknown specification constant 'minimum_income' in domain bound",
    ):
        ToetraValidator().validate(program, tracer=ValidationTracer(enabled=False))


def test_explicit_feature_in_arithmetic_domain_bound_is_bound_recursively() -> None:
    program = _build_and_validate("""
        model := "model.onnx"
        target := MyTarget

        margin := 1

        [LOGIC]:
        forall x0
            with domain(x0.a: [x0.b - margin, x0.b + margin])
            => target <= 1
        """)

    scope = program.body[0].rule.scope
    assert isinstance(scope, QuantifierExprNode)
    domain = scope.domain
    assert domain is not None

    interval = domain.entries[0].constraint
    assert isinstance(interval, IntervalDomainNode)
    assert isinstance(interval.lower, BinaryArithmeticNode)
    assert isinstance(interval.lower.left, AttributeNode)
    assert interval.lower.left.semantic is not None
    assert interval.lower.left.semantic.resolved_entity == "x0"
    assert isinstance(interval.lower.right, ConstantNode)
    assert interval.lower.right.value == 1


def test_finite_set_name_uses_constant_or_symbolic_literal_by_lookup() -> None:
    program = _build_and_validate("""
        model := "model.onnx"
        target := MyTarget

        preferred_region := "EU"

        [LOGIC]:
        forall applicant
            with domain(applicant.region: {preferred_region, US})
            => target <= 1
        """)

    scope = program.body[0].rule.scope
    assert isinstance(scope, QuantifierExprNode)
    domain = scope.domain
    assert domain is not None

    finite_set = domain.entries[0].constraint
    assert isinstance(finite_set, FiniteSetDomainNode)
    assert isinstance(finite_set.values[0], ConstantNode)
    assert finite_set.values[0].value == "EU"
    assert finite_set.values[0].semantic is not None
    assert finite_set.values[0].semantic.resolved_symbol is not None
    assert finite_set.values[0].semantic.resolved_symbol.name == "preferred_region"
    assert finite_set.values[1] == SymbolLiteralNode(name="US")
