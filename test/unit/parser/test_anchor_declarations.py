from __future__ import annotations

import pytest
from lark.exceptions import UnexpectedInput
from dsl.parser.parser import parse_forml_code
from test.unit.parser._point_binding_helpers import (
    direct_trees,
    program,
    single_tree,
    token_text,
)

# ---------------------------------------------------------------------------
# PAR-ANCH-* — global inline anchor declarations
# ---------------------------------------------------------------------------


def test_par_anchor_001_inline_anchor_parses_in_completeprogram() -> None:
    tree = parse_forml_code(
        program(
            declarations="anchor x0 := { age: 42 }",
            body="target[x0] <= 7",
        )
    )

    declaration = single_tree(tree, "anchor_declaration")
    assert token_text(direct_trees(declaration, "identifier")[0]) == "x0"
    assert len(list(declaration.find_data("anchor_entry"))) == 1


def test_par_anchor_002_feature_and_literal_order_is_preserved() -> None:
    tree = parse_forml_code(
        program(
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
    )

    entries = list(tree.find_data("anchor_entry"))
    assert [token_text(direct_trees(entry, "identifier")[0]) for entry in entries] == [
        "age",
        "income",
        "enabled",
        "segment",
    ]
    assert [token_text(single_tree(entry, "anchor_literal")) for entry in entries] == [
        "42",
        "-5.5",
        "true",
        '"A"',
    ]


def test_par_anchor_003_trailing_comma_is_accepted() -> None:
    parse_forml_code(
        program(
            declarations="anchor x0 := { age: 42, }",
            body="target[x0] <= 7",
        )
    )


@pytest.mark.parametrize(
    "declaration",
    [
        pytest.param("anchor x0 := {}", id="PAR-ANCH-004-empty-block"),
        pytest.param("anchor := { age: 42 }", id="PAR-ANCH-005-missing-name"),
        pytest.param(
            "anchor x0 := { x0.age = 42 }",
            id="PAR-ANCH-006-qualified-assignment",
        ),
        pytest.param(
            "anchor x0 := { age 42 }",
            id="PAR-ANCH-007-missing-colon",
        ),
    ],
)
def test_invalid_inline_anchor_surface_is_rejected(declaration: str) -> None:
    with pytest.raises(UnexpectedInput):
        parse_forml_code(program(declarations=declaration, body="target <= 7"))


def test_par_anchor_008_duplicate_feature_spelling_is_preserved_for_semantics() -> None:
    tree = parse_forml_code(
        program(
            declarations="anchor x0 := { age: 42, age: 45 }",
            body="target[x0] <= 7",
        )
    )

    entries = list(tree.find_data("anchor_entry"))
    assert [token_text(direct_trees(entry, "identifier")[0]) for entry in entries] == [
        "age",
        "age",
    ]


def test_par_anchor_009_anchor_after_first_property_is_rejected() -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    target <= 7

    anchor x0 := { age: 42 }
    """

    with pytest.raises(UnexpectedInput):
        parse_forml_code(source)
