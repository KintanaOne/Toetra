from __future__ import annotations

from toetra._compiler.ast.nodes.assertion import AndNode, ComparisonNode
from toetra._compiler.ast.nodes.expressions import QuantifierExprNode
from toetra._compiler.ast.nodes.neighborhood import NeighborhoodMembershipNode
from toetra._compiler.ast.nodes.primitives import ConstantNode
from toetra._compiler.semantic.types.enums import EnumDataType
from test.unit.builder._point_binding_helpers import build_program


def test_ast_where_001_generic_restriction_is_separate_from_assertion() -> None:
    program = build_program(body="""
        forall x0, x1
        where (x1.income >= x0.income and x1.age == x0.age)
        => target[x1] <= target[x0]
        """)

    scope = program.body[0].rule.scope
    assertion = program.body[0].rule.assertion.root
    assert isinstance(scope, QuantifierExprNode)
    assert scope.restriction is not None
    assert isinstance(scope.restriction.expression, AndNode)
    assert isinstance(assertion, ComparisonNode)
    assert scope.restriction.expression is not assertion


def test_ast_nbh_001_membership_is_structured() -> None:
    program = build_program(
        declarations="anchor x0 := { age: 42 }",
        body="""
        forall x1
        where x1 in neighborhood(of = x0, metric = Linf, eps = 0.05)
        => target[x1] >= target[x0]
        """,
        property_type="ROBUSTNESS",
    )

    scope = program.body[0].rule.scope
    assert isinstance(scope, QuantifierExprNode)
    assert scope.restriction is not None
    membership = scope.restriction.expression
    assert isinstance(membership, NeighborhoodMembershipNode)
    assert membership.candidate == "x1"
    assert membership.anchor == "x0"
    assert membership.metric == "Linf"
    assert membership.epsilon == ConstantNode(0.05, EnumDataType.FLOAT)
