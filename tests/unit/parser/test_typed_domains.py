from __future__ import annotations

from collections.abc import Callable

import pytest
from lark import Token, Tree
from toetra._compiler.parser.errors import ParserError

from toetra._compiler.parser.parser import parse_toetra_code


@pytest.mark.parametrize(
    ("source", "expected_rule"),
    [
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.a: [0, 3]
                )
                => target <= 7
                using Z3
            """,
            "closed_closed_interval",
            id="closed-closed",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.a: ]0, 3]
                )
                => target <= 7
                using Z3
            """,
            "open_closed_interval",
            id="open-closed",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.a: [0, 3[
                )
                => target <= 7
                using Z3
            """,
            "closed_open_interval",
            id="closed-open",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.a: ]0, 3[
                )
                => target <= 7
                using Z3
            """,
            "open_open_interval",
            id="open-open",
        ),
    ],
)
def test_interval_delimiters_are_preserved_by_named_cst_rules(
    source: str,
    expected_rule: str,
    single_cst_tree: Callable[[Tree, str], Tree],
) -> None:
    tree = parse_toetra_code(source)
    interval_domain = single_cst_tree(tree, "interval_domain")

    interval_children = [
        child.data for child in interval_domain.children if isinstance(child, Tree)
    ]

    assert interval_children == [expected_rule]


@pytest.mark.parametrize(
    ("source", "expected_values"),
    [
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.a: {0, 7}
                )
                => target <= 7
                using Z3
            """,
            ["0", "7"],
            id="numeric-set",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.region: {EU, US}
                )
                => target <= 7
                using Z3
            """,
            ["EU", "US"],
            id="symbolic-set",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.category: {"A", "B"}
                )
                => target <= 7
                using Z3
            """,
            ['"A"', '"B"'],
            id="string-set",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.enabled: {true, false}
                )
                => target <= 7
                using Z3
            """,
            ["true", "false"],
            id="boolean-set",
        ),
    ],
)
def test_finite_set_values_and_order_are_preserved(
    source: str,
    expected_values: list[str],
    single_cst_tree: Callable[[Tree, str], Tree],
    first_cst_token: Callable[[Tree], Token],
) -> None:
    tree = parse_toetra_code(source)
    finite_set = single_cst_tree(tree, "finite_set_domain")

    values = [
        str(first_cst_token(child))
        for child in finite_set.children
        if isinstance(child, Tree) and child.data == "finite_set_value"
    ]

    assert values == expected_values


def test_domain_accepts_multiple_entries_and_trailing_comma() -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0
        with domain(
            x0.a: [0, 3],
            x0.region: {EU, US},
        )
        => target <= 7
        using Z3
    """

    tree = parse_toetra_code(source)

    assert len(list(tree.find_data("domain_entry"))) == 2


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain()
                => target <= 7
                using Z3
            """,
            id="empty-domain",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.a: {}
                )
                => target <= 7
                using Z3
            """,
            id="empty-finite-set",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            forall x0
                with domain(
                    x0.a: (0, 3]
                )
                => target <= 7
                using Z3
            """,
            id="mixed-parenthesis-interval",
        ),
    ],
)
def test_invalid_domain_syntax_is_rejected(source: str) -> None:
    with pytest.raises(ParserError):
        parse_toetra_code(source)


def test_unqualified_domain_subject_parses_for_semantic_rejection(
    single_cst_tree: Callable[[Tree, str], Tree],
    first_cst_token: Callable[[Tree], Token],
) -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0
        with domain(
            a: [0, 3]
        )
        => target <= 7
        using Z3
    """

    tree = parse_toetra_code(source)
    domain_entry = single_cst_tree(tree, "domain_entry")
    subject = next(
        child
        for child in domain_entry.children
        if isinstance(child, Tree) and child.data == "attribute"
    )

    assert [str(first_cst_token(node)) for node in subject.find_data("identifier")] == [
        "a"
    ]


def test_target_bound_parses_for_semantic_rejection() -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0
        with domain(
            x0.a: [0, target]
        )
        => target <= 7
        using Z3
    """

    tree = parse_toetra_code(source)

    assert len(list(tree.find_data("target_ref"))) == 2
