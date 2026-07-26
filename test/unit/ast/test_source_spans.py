from __future__ import annotations

from toetra._compiler.ast.nodes.source import SourceSpan
from test.unit.builder._point_binding_helpers import build_program


def test_source_span_does_not_change_ast_structural_equality() -> None:
    first = build_program(body="forall x0 => target <= 7").body[0].rule.scope
    second = build_program(body="forall x0 => target <= 7").body[0].rule.scope

    assert first.source_span is not None
    assert second.source_span is not None
    first.source_span = SourceSpan(100, 1, 100, 10)
    assert first == second
