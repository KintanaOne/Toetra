from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.domain import (
    FiniteSetDomainNode,
    IntervalDomainNode,
)
from toetra._compiler.ast.nodes.expressions import AtExprNode, QuantifierExprNode
from toetra._compiler.ast.nodes.primitives import (
    AttributeNode,
    BinaryArithmeticNode,
    ConstantNode,
    NameRefNode,
)
from toetra._compiler.builder.program import parse_program
from toetra._language.vocabulary.domains import EnumBoundaryKind
from toetra._language.vocabulary.operators import EnumArithmeticOperator
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.types.enums import EnumDataType


def build(source: str):
    return parse_program(parse_toetra_code(source))


def program_with_domain(entries: str, *, scope: str = "forall x0") -> str:
    return f"""
model := "model.onnx"
target := MyTarget

[LOGIC]:
{scope}
    with domain(
        {entries}
    )
    => target <= 7
"""


@pytest.mark.parametrize(
    ("syntax", "lower_boundary", "upper_boundary"),
    [
        ("[0.0, 3.0]", EnumBoundaryKind.CLOSED, EnumBoundaryKind.CLOSED),
        ("]0.0, 3.0]", EnumBoundaryKind.OPEN, EnumBoundaryKind.CLOSED),
        ("[0.0, 3.0[", EnumBoundaryKind.CLOSED, EnumBoundaryKind.OPEN),
        ("]0.0, 3.0[", EnumBoundaryKind.OPEN, EnumBoundaryKind.OPEN),
    ],
)
def test_builds_all_interval_boundary_kinds(
    syntax: str,
    lower_boundary: EnumBoundaryKind,
    upper_boundary: EnumBoundaryKind,
):
    program = build(program_with_domain(f"x0.a: {syntax}"))
    scope = program.body[0].rule.scope

    assert isinstance(scope, QuantifierExprNode)
    assert scope.variable == "x0"
    assert scope.domain is not None
    assert len(scope.domain.entries) == 1

    entry = scope.domain.entries[0]
    assert entry.subject.entity == "x0"
    assert entry.subject.feature == "a"
    assert isinstance(entry.constraint, IntervalDomainNode)
    assert entry.constraint.lower_boundary == lower_boundary
    assert entry.constraint.upper_boundary == upper_boundary
    assert entry.constraint.lower == ConstantNode(0.0, EnumDataType.FLOAT)
    assert entry.constraint.upper == ConstantNode(3.0, EnumDataType.FLOAT)


def test_builds_symbolic_finite_set_without_turning_names_into_features():
    program = build(program_with_domain("x0.segment: {retail, corporate}"))
    scope = program.body[0].rule.scope

    assert isinstance(scope, QuantifierExprNode)
    assert scope.domain is not None
    constraint = scope.domain.entries[0].constraint

    assert isinstance(constraint, FiniteSetDomainNode)
    assert constraint.values == [
        NameRefNode("retail"),
        NameRefNode("corporate"),
    ]


def test_builds_typed_quoted_and_numeric_finite_sets():
    source = program_with_domain(
        'x0.region: {"EU", "US"},\n        x0.score: {0.0, 7.0}'
    )
    program = build(source)
    scope = program.body[0].rule.scope

    assert isinstance(scope, QuantifierExprNode)
    assert scope.domain is not None
    assert len(scope.domain.entries) == 2

    regions = scope.domain.entries[0].constraint
    scores = scope.domain.entries[1].constraint

    assert isinstance(regions, FiniteSetDomainNode)
    assert regions.values == [
        ConstantNode("EU", EnumDataType.STRING),
        ConstantNode("US", EnumDataType.STRING),
    ]
    assert isinstance(scores, FiniteSetDomainNode)
    assert scores.values == [
        ConstantNode(0.0, EnumDataType.FLOAT),
        ConstantNode(7.0, EnumDataType.FLOAT),
    ]


def test_preserves_domain_entry_order_and_subject_qualification():
    source = program_with_domain(
        "x0.a: [0, 3],\n" "        x0.b: {one, two},\n" "        x0.c: ]0, 3["
    )
    program = build(source)
    scope = program.body[0].rule.scope

    assert isinstance(scope, QuantifierExprNode)
    assert scope.domain is not None
    assert [
        (entry.subject.entity, entry.subject.feature) for entry in scope.domain.entries
    ] == [
        ("x0", "a"),
        ("x0", "b"),
        ("x0", "c"),
    ]


def test_domain_is_built_for_local_at_scope_too():
    program = build(
        program_with_domain(
            'x0.sex: {"male", "female"}',
            scope="at x0",
        )
    )
    scope = program.body[0].rule.scope

    assert isinstance(scope, AtExprNode)
    assert scope.domain is not None
    assert scope.domain.entries[0].subject.entity == "x0"
    assert scope.domain.entries[0].subject.feature == "sex"


def test_builds_arithmetic_interval_bounds():
    source = program_with_domain("x0.a: [x0.b - 1, x0.b + 1]")
    program = build(source)
    scope = program.body[0].rule.scope

    assert isinstance(scope, QuantifierExprNode)
    assert scope.domain is not None

    interval = scope.domain.entries[0].constraint
    assert isinstance(interval, IntervalDomainNode)
    assert isinstance(interval.lower, BinaryArithmeticNode)
    assert interval.lower.operator is EnumArithmeticOperator.SUB
    assert interval.lower.left == AttributeNode(
        entity="x0",
        feature="b",
        path=["x0", "b"],
    )
    assert isinstance(interval.lower.right, ConstantNode)

    assert isinstance(interval.upper, BinaryArithmeticNode)
    assert interval.upper.operator is EnumArithmeticOperator.ADD
