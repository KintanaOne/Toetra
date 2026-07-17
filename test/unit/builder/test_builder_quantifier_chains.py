from __future__ import annotations

import pytest

from dsl.ast.nodes.expressions import QuantifierExprNode
from test.unit.builder._point_binding_helpers import build_program


def test_ast_qp_001_grouped_identifiers_preserve_source_order() -> None:
    program = build_program(body="forall x0, x1 => target[x1] >= target[x0]")

    scope = program.body[0].rule.scope
    assert isinstance(scope, QuantifierExprNode)
    assert [(binder.quantifier, binder.variables) for binder in scope.binders] == [
        ("forall", ["x0", "x1"])
    ]


def test_ast_qp_002_mixed_binder_chain_is_ordered_not_mapped() -> None:
    program = build_program(body="forall x0 exists x1 => target[x1] >= target[x0]")

    scope = program.body[0].rule.scope
    assert isinstance(scope, QuantifierExprNode)
    assert [(binder.quantifier, binder.variables) for binder in scope.binders] == [
        ("forall", ["x0"]),
        ("exists", ["x1"]),
    ]


def test_legacy_projection_remains_available_for_one_point_scope() -> None:
    scope = build_program(body="forall x0 => target <= 7").body[0].rule.scope
    assert isinstance(scope, QuantifierExprNode)
    assert scope.quantifier == "forall"
    assert scope.variable == "x0"


def test_legacy_projection_rejects_multi_point_scope_instead_of_guessing() -> None:
    scope = build_program(body="forall x0, x1 => target[x0] <= 7").body[0].rule.scope
    assert isinstance(scope, QuantifierExprNode)

    with pytest.raises(ValueError, match="exactly one binder and one point"):
        _ = scope.variable
