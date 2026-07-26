from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.ast.nodes.primitives import BinaryArithmeticNode, TargetRefNode
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.semantic.context.restrictions import RestrictionOrigin
from toetra._compiler.semantic.context.scope import SemanticScope
from toetra._compiler.semantic.symbols.point import PointBindingKind
from tests.support.semantic_restrictions import (
    inline_anchor,
    parse_and_validate,
)


def _source(*, anchors: str | None = None, candidate: str = "x1") -> str:
    declarations = anchors if anchors is not None else inline_anchor()
    return f"""
        model := "model.joblib"
        target := score
        {declarations}

        [ROBUSTNESS]:
        at x0 with {candidate} in neighborhood(
            metric = Linf,
            eps = 0.1
        )
        => target[{candidate}] - target[x0] <= 0.2
        """


def test_low_at_001_lowers_to_fresh_universal_candidate_and_restriction() -> None:
    program = parse_and_validate(_source())
    semantic = program.body[0].semantic
    assert semantic is not None
    assert semantic.context is not None
    context = semantic.context

    assert context.type is SemanticScope.QUANTIFIER
    assert context.quantifier_chain == ("forall",)
    assert len(context.binder_frames) == 1
    frame = context.binder_frames[0]
    assert frame.point.name == "x1"
    assert frame.point.binding_kind is PointBindingKind.UNIVERSAL
    assert frame.generated is True
    assert context.canonical_restriction is not None


def test_low_at_002_undeclared_anchor_is_rejected() -> None:
    with pytest.raises(ParserError, match="undeclared anchor 'x0'"):
        parse_and_validate(_source(anchors=""))


def test_low_at_003_candidate_collision_is_rejected() -> None:
    anchors = inline_anchor("x0") + inline_anchor("x1")
    with pytest.raises(ParserError, match="collides with a visible point"):
        parse_and_validate(_source(anchors=anchors))


def test_low_at_004_generated_artifacts_retain_sugar_provenance() -> None:
    program = parse_and_validate(_source())
    scope = program.body[0].rule.scope
    semantic = program.body[0].semantic
    assert semantic is not None
    assert semantic.context is not None
    context = semantic.context

    assert scope.source_span is not None
    assert context.binder_frames[0].source_span == scope.source_span
    assert context.binder_frames[0].generated is True
    assert context.restriction is not None
    assert context.restriction.source_span == scope.source_span
    assert context.restriction_provenance is not None
    assert context.restriction_provenance.origin is RestrictionOrigin.AT_SUGAR
    assert context.restriction_provenance.source_span == scope.source_span


def test_low_at_005_both_indexed_evaluations_are_preserved() -> None:
    program = parse_and_validate(_source())
    root = program.body[0].rule.assertion.root
    assert isinstance(root, ComparisonNode)
    assert isinstance(root.left, BinaryArithmeticNode)
    assert isinstance(root.left.left, TargetRefNode)
    assert isinstance(root.left.right, TargetRefNode)

    candidate = root.left.left.semantic
    anchor = root.left.right.semantic
    assert candidate is not None
    assert anchor is not None
    assert candidate.resolved_point is not None
    assert anchor.resolved_point is not None
    assert candidate.resolved_point.name == "x1"
    assert anchor.resolved_point.name == "x0"
    assert candidate.resolved_evaluation is not anchor.resolved_evaluation


def test_at_sugar_and_explicit_form_have_equal_canonical_semantics() -> None:
    sugar = parse_and_validate(_source())
    explicit = parse_and_validate(f"""
        model := "model.joblib"
        target := score
        {inline_anchor()}

        [ROBUSTNESS]:
        forall x1
        where x1 in neighborhood(
            of = x0,
            metric = Linf,
            eps = 0.1
        )
        => target[x1] - target[x0] <= 0.2
        """)

    sugar_semantic = sugar.body[0].semantic
    explicit_semantic = explicit.body[0].semantic
    assert sugar_semantic is not None
    assert explicit_semantic is not None
    assert sugar_semantic.restriction_root == explicit_semantic.restriction_root
    assert sugar_semantic.logical_root == explicit_semantic.logical_root
    assert sugar_semantic.verification_root == explicit_semantic.verification_root
