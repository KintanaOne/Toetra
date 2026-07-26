from __future__ import annotations

import pytest

from toetra._compiler.parser.errors import ParserError
from toetra._compiler.semantic.context.scope import SemanticScope
from ._point_binding_helpers import (
    build_and_validate,
    semantic_context,
)


def test_fairness_accepts_explicit_two_point_quantifier_environment() -> None:
    program = build_and_validate("""
        model := "model.joblib"
        target := score

        [FAIRNESS]:
        forall x0, x1 => x0.a == x1.a
        """)

    context = semantic_context(program)
    assert context.type is SemanticScope.QUANTIFIER
    assert context.point_environment.names() == ("x0", "x1")


def test_fairness_rejects_a_single_visible_point_without_scope_enum_gating() -> None:
    with pytest.raises(ParserError, match="requires at least two visible points"):
        build_and_validate("""
            model := "model.joblib"
            target := score

            [FAIRNESS]:
            forall x0 => x0.a == x0.a
            """)
