from __future__ import annotations

from types import MappingProxyType
from typing import Any, cast

import pytest

from toetra._compiler.semantic.symbols.point import PointBindingKind, PointSymbol
from tests.support.semantic_anchors import validate_program


def test_sem_anchor_001_registers_unique_inline_anchor() -> None:
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

    point = context.point_environment.resolve("baseline")
    assert isinstance(point, PointSymbol)
    assert point.binding_kind is PointBindingKind.INLINE_ANCHOR
    assert point.is_anchor
    assert point.lexical_depth == 0
    assert point.declaration is program.anchors[0]
    assert isinstance(point.concrete_values, MappingProxyType)
    assert point.concrete_values["age"].value == 42
    assert point.concrete_values["income"].value == 55000
    assert point.concrete_values["active"].value is True
    assert tuple(point.feature_schema or ()) == ("age", "income", "active")

    immutable_values = cast(Any, point.concrete_values)
    with pytest.raises(TypeError):
        immutable_values["age"] = immutable_values["age"]


def test_sem_anchor_002_registers_unresolved_referenced_anchor() -> None:
    program = validate_program("""
        model := "model.onnx"
        target := score

        anchor customer := ref(
            key = "customer_id",
            value = "C-1842"
        )

        [BOUND]:
        check_at customer => target <= 1
        """)

    annotation = program.body[0].semantic
    assert annotation is not None
    context = annotation.context
    assert context is not None

    point = context.point_environment.resolve("customer")
    assert isinstance(point, PointSymbol)
    assert point.binding_kind is PointBindingKind.REFERENCED_ANCHOR
    assert point.concrete_values is None
    assert point.reference is not None
    assert point.reference.key == "customer_id"
    assert point.reference.value.value == "C-1842"
    assert point.declaration is program.anchors[0]


def test_sem_anchor_008_accepts_lookup_key_outside_model_features() -> None:
    program = validate_program("""
        model := "model.onnx"
        target := score

        anchor customer := ref(
            key = "external_customer_id",
            value = 1842
        )

        [BOUND]:
        check_at customer => target <= 1
        """)

    annotation = program.body[0].semantic
    assert annotation is not None
    context = annotation.context
    assert context is not None
    point = context.point_environment.resolve("customer")
    assert point is not None
    assert point.reference is not None
    assert point.reference.key == "external_customer_id"
    assert "external_customer_id" not in (point.feature_schema or {})
