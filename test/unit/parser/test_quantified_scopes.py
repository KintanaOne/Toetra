from __future__ import annotations

from collections.abc import Callable

import pytest
from lark import Token, Tree
from lark.exceptions import UnexpectedInput

from dsl.parser.parser import parse_toetra_code


@pytest.mark.parametrize(
    ("source", "expected_quantifier", "expected_identifier"),
    [
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                => target <= 7
                using Z3
            """,
            "forall",
            "x0",
            id="forall-word",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            exists candidate
                => target <= 7
                using Z3
            """,
            "exists",
            "candidate",
            id="exists-word",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            ∀ sample
                => target <= 7
                using Z3
            """,
            "∀",
            "sample",
            id="forall-symbol",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            ∃ witness
                => target <= 7
                using Z3
            """,
            "∃",
            "witness",
            id="exists-symbol",
        ),
    ],
)
def test_quantifier_requires_and_preserves_explicit_identifier(
    source: str,
    expected_quantifier: str,
    expected_identifier: str,
    single_cst_tree: Callable[[Tree, str], Tree],
    first_cst_token: Callable[[Tree], Token],
) -> None:
    tree = parse_toetra_code(source)
    quantifier_expr = single_cst_tree(tree, "quantifier_expr")

    quantifier = next(
        child
        for child in quantifier_expr.children
        if isinstance(child, Tree) and child.data == "quantifier"
    )
    identifier = next(
        child
        for child in quantifier_expr.children
        if isinstance(child, Tree) and child.data == "identifier"
    )

    assert str(first_cst_token(quantifier)) == expected_quantifier
    assert str(first_cst_token(identifier)) == expected_identifier


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall
                => target <= 7
                using Z3
            """,
            id="forall-word-without-identifier",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            exists
                => target <= 7
                using Z3
            """,
            id="exists-word-without-identifier",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            ∀
                => target <= 7
                using Z3
            """,
            id="forall-symbol-without-identifier",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            ∃
                => target <= 7
                using Z3
            """,
            id="exists-symbol-without-identifier",
        ),
    ],
)
def test_quantifier_without_identifier_is_rejected(source: str) -> None:
    with pytest.raises(UnexpectedInput):
        parse_toetra_code(source)
