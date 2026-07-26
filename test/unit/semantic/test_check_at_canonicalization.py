from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.ast.nodes.expressions import CheckAtExprNode
from toetra._compiler.ast.nodes.primitives import TargetRefNode
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.semantic.context.points import PointEnvironment
from toetra._compiler.semantic.core.lhs import LHSValidator
from toetra._compiler.semantic.symbols.point import PointBindingKind, PointSymbol
from test.unit.semantic.restriction_helpers import (
    inline_anchor,
    numeric_schema,
    parse_and_validate,
)


def test_low_chk_001_declared_anchor_sets_default_without_quantifier() -> None:
    program = parse_and_validate(f"""
        model := "model.joblib"
        target := score
        {inline_anchor()}

        [BOUND]:
        check_at x0 => target <= 7
        """)

    semantic = program.body[0].semantic
    assert semantic is not None
    assert semantic.context is not None
    context = semantic.context

    assert context.selected_default_point is not None
    assert context.selected_default_point.name == "x0"
    assert context.binder_frames == ()
    assert context.quantifier_chain == ()
    assert context.legacy_scope_compatibility is False


def test_low_chk_002_unknown_anchor_is_rejected_when_anchors_are_declared() -> None:
    with pytest.raises(ParserError, match="unknown anchor 'missing'"):
        parse_and_validate(f"""
            model := "model.joblib"
            target := score
            {inline_anchor()}

            [BOUND]:
            check_at missing => target <= 7
            """)


def test_low_chk_003_symbolic_point_cannot_be_selected() -> None:
    symbolic = PointSymbol(
        name="x0",
        binding_kind=PointBindingKind.UNIVERSAL,
        declaration=object(),
    )
    environment = PointEnvironment()
    environment.register_lexical(symbolic, quantifier="forall")

    with pytest.raises(Exception, match="is not an anchor"):
        LHSValidator(model_schema=numeric_schema()).validate(
            CheckAtExprNode(variable="x0"),
            point_environment=environment,
        )


def test_low_chk_004_short_target_resolves_to_selected_anchor() -> None:
    program = parse_and_validate(f"""
        model := "model.joblib"
        target := score
        {inline_anchor()}

        [BOUND]:
        check_at x0 => target <= 7
        """)

    root = program.body[0].rule.assertion.root
    assert isinstance(root, ComparisonNode)
    assert isinstance(root.left, TargetRefNode)
    assert root.left.semantic is not None
    assert root.left.semantic.resolved_point is not None
    assert root.left.semantic.resolved_point.name == "x0"
