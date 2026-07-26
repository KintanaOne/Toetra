from __future__ import annotations

from toetra._compiler.ast.nodes.anchors import (
    AnchorReferenceBindingNode,
    InlineAnchorBindingNode,
)
from toetra._compiler.semantic.types.enums import EnumDataType
from tests.support.program_builder import build_program


def test_ast_anchor_001_inline_anchor_is_structured_and_ordered() -> None:
    program = build_program(
        declarations="""
        anchor x0 := {
            age: 42,
            income: -5.5,
            enabled: true,
            segment: "A"
        }
        """,
        body="target[x0] <= 7",
    )

    assert [anchor.name for anchor in program.anchors] == ["x0"]
    binding = program.anchors[0].binding
    assert isinstance(binding, InlineAnchorBindingNode)
    assert [entry.feature for entry in binding.entries] == [
        "age",
        "income",
        "enabled",
        "segment",
    ]
    assert [entry.value.value for entry in binding.entries] == [42, -5.5, True, "A"]
    assert [entry.value.dtype for entry in binding.entries] == [
        EnumDataType.INT,
        EnumDataType.FLOAT,
        EnumDataType.BOOL,
        EnumDataType.STRING,
    ]


def test_ast_anchor_002_reference_arguments_remain_named_and_ordered() -> None:
    program = build_program(
        declarations='anchor x0 := ref(value = "42", key = "customer_id")',
        body="target[x0] <= 7",
    )

    binding = program.anchors[0].binding
    assert isinstance(binding, AnchorReferenceBindingNode)
    assert [argument.name for argument in binding.arguments] == ["value", "key"]
    assert [argument.value.value for argument in binding.arguments] == [
        "42",
        "customer_id",
    ]
    assert all(
        argument.value.dtype is EnumDataType.STRING for argument in binding.arguments
    )


def test_anchor_duplicates_are_not_collapsed_by_the_builder() -> None:
    program = build_program(
        declarations="anchor x0 := { age: 42, age: 45 }",
        body="target[x0] <= 7",
    )

    binding = program.anchors[0].binding
    assert isinstance(binding, InlineAnchorBindingNode)
    assert [entry.feature for entry in binding.entries] == ["age", "age"]
    assert [entry.value.value for entry in binding.entries] == [42, 45]
