from __future__ import annotations

import pytest
from lark.exceptions import UnexpectedInput
from toetra._compiler.parser.parser import parse_toetra_code
from tests.support.parser_points import (
    program,
    single_tree,
    token_text,
)

# ---------------------------------------------------------------------------
# PAR-TGT-* and PAR-DIR-* — indexed output and direct property body
# ---------------------------------------------------------------------------


def test_par_tgt_001_indexed_target_preserves_point_identifier() -> None:
    tree = parse_toetra_code(program(body="forall x0 => target[x0] <= 7"))
    target = single_tree(tree, "target_ref")
    assert token_text(single_tree(target, "identifier")) == "x0"


def test_par_tgt_002_unindexed_target_remains_distinct() -> None:
    tree = parse_toetra_code(program(body="forall x0 => target <= 7"))
    target = single_tree(tree, "target_ref")
    assert not list(target.find_data("identifier"))


@pytest.mark.parametrize(
    "target",
    [
        pytest.param("target[]", id="PAR-TGT-003-empty-index"),
        pytest.param("target[x0, x1]", id="PAR-TGT-004-multiple-indices"),
        pytest.param('target["x0"]', id="PAR-TGT-005-string-index"),
    ],
)
def test_invalid_target_index_surface_is_rejected(target: str) -> None:
    with pytest.raises(UnexpectedInput):
        parse_toetra_code(program(body=f"forall x0 => {target} <= 7"))


def test_par_dir_001_direct_assertion_has_no_scope_implication() -> None:
    tree = parse_toetra_code(
        program(
            declarations="anchor x0 := { age: 42 }",
            body="target[x0] <= 7 using Z3",
        )
    )
    property_node = single_tree(tree, "property")

    assert not list(property_node.find_data("property_expr"))
    assert not list(property_node.find_data("property_imply"))
    assert len(list(property_node.find_data("comparison_expr"))) == 1


def test_par_dir_002_scoped_property_retains_explicit_implication() -> None:
    tree = parse_toetra_code(program(body="forall x0 => target <= 7 using Z3"))
    property_node = single_tree(tree, "property")

    assert len(list(property_node.find_data("property_expr"))) == 1
    assert len(list(property_node.find_data("property_imply"))) == 1
