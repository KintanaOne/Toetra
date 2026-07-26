from __future__ import annotations

from toetra._compiler.semantic.context.scope import SemanticScope
from toetra._compiler.semantic.symbols.point import PointSymbol
from test.unit.semantic.anchor_helpers import validate_program


def test_global_anchor_is_seeded_into_legacy_context_projection() -> None:
    program = validate_program("""
        model := "model.onnx"
        target := score

        anchor baseline := {
            age: 42,
            income: 55000,
            active: true
        }

        [BOUND]:
        check_at baseline => target <= 1
        """)

    annotation = program.body[0].semantic
    assert annotation is not None
    context = annotation.context
    assert context is not None
    assert context.type is SemanticScope.POINTWISE
    assert context.variables["baseline"] == "anchor"

    point = context.point_environment.resolve("baseline")
    assert isinstance(point, PointSymbol)
    assert context.symbol_table.resolve("baseline") is point


def test_each_property_gets_isolated_environment_with_same_global_identity() -> None:
    program = validate_program("""
        model := "model.onnx"
        target := score

        anchor baseline := {
            age: 42,
            income: 55000,
            active: true
        }

        [BOUND]:
        check_at baseline => target <= 1

        [LOGIC]:
        check_at baseline => age >= 18
        """)

    first_annotation = program.body[0].semantic
    second_annotation = program.body[1].semantic
    assert first_annotation is not None
    assert second_annotation is not None
    first = first_annotation.context
    second = second_annotation.context
    assert first is not None
    assert second is not None
    assert first.point_environment is not second.point_environment
    assert first.point_environment.resolve(
        "baseline"
    ) is second.point_environment.resolve("baseline")
