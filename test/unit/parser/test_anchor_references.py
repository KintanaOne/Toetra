from __future__ import annotations

from lark import Tree
import pytest
from lark.exceptions import UnexpectedInput
from dsl.parser.parser import parse_forml_code
from test.unit.parser._point_binding_helpers import (
    program,
    single_tree,
)

# ---------------------------------------------------------------------------
# PAR-REF-* — single-source referenced anchor syntax
# ---------------------------------------------------------------------------


def test_par_ref_001_named_key_and_value_arguments_parse() -> None:
    tree = parse_forml_code(
        program(
            declarations='anchor x0 := ref(key = "id", value = "42")',
            body="target[x0] <= 7",
        )
    )

    anchor_ref = single_tree(tree, "anchor_ref")
    assert [
        child.data
        for argument in anchor_ref.find_data("anchor_ref_argument")
        for child in argument.children
        if isinstance(child, Tree)
    ] == ["anchor_ref_key_argument", "anchor_ref_value_argument"]


def test_par_ref_002_multiline_reference_parses() -> None:
    parse_forml_code(
        program(
            declarations="""
            anchor x0 := ref(
                key = "id",
                value = "42",
            )
            """,
            body="target[x0] <= 7",
        )
    )


def test_par_ref_003_missing_key_is_preserved_for_semantic_rejection() -> None:
    tree = parse_forml_code(
        program(
            declarations='anchor x0 := ref(value = "42")',
            body="target[x0] <= 7",
        )
    )

    assert len(list(tree.find_data("anchor_ref_value_argument"))) == 1
    assert not list(tree.find_data("anchor_ref_key_argument"))


def test_par_ref_004_duplicate_key_is_preserved_for_semantic_rejection() -> None:
    tree = parse_forml_code(
        program(
            declarations='anchor x0 := ref(key = "id", key = "other")',
            body="target[x0] <= 7",
        )
    )

    assert len(list(tree.find_data("anchor_ref_key_argument"))) == 2


@pytest.mark.parametrize(
    "binding",
    [
        pytest.param('ref("id", "42")', id="PAR-REF-005-positional"),
        pytest.param(
            'ref(source = "validation", key = "id", value = "42")',
            id="PAR-REF-006-deferred-source",
        ),
    ],
)
def test_unsupported_reference_argument_surface_is_rejected(binding: str) -> None:
    with pytest.raises(UnexpectedInput):
        parse_forml_code(
            program(
                declarations=f"anchor x0 := {binding}",
                body="target[x0] <= 7",
            )
        )
