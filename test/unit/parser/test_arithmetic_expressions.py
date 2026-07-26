from __future__ import annotations

from collections.abc import Callable

from lark import Tree

from toetra._compiler.parser.parser import parse_toetra_code


def test_arithmetic_precedence_is_preserved_in_cst(
    single_cst_tree: Callable[[Tree, str], Tree],
    cst_operator_values: Callable[[Tree, str], list[str]],
) -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0
        => a + b * 2 <= target
        using Z3
    """

    tree = parse_toetra_code(source)
    comparison = single_cst_tree(tree, "comparison_expr")
    left = next(
        child
        for child in comparison.children
        if isinstance(child, Tree) and child.data == "scalar_expression"
    )
    additive = single_cst_tree(left, "additive_expr")

    direct_multiplicative = [
        child
        for child in additive.children
        if isinstance(child, Tree) and child.data == "multiplicative_expr"
    ]

    assert len(direct_multiplicative) == 2
    assert cst_operator_values(additive, "additive_operator") == ["+"]
    assert (
        cst_operator_values(direct_multiplicative[0], "multiplicative_operator") == []
    )
    assert cst_operator_values(direct_multiplicative[1], "multiplicative_operator") == [
        "*"
    ]


def test_unary_sign_is_preserved_in_cst(
    cst_operator_values: Callable[[Tree, str], list[str]],
) -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0
        => -a + b <= target
        using Z3
    """

    tree = parse_toetra_code(source)

    assert cst_operator_values(tree, "unary_operator") == ["-"]


def test_parenthesized_arithmetic_group_is_preserved_in_cst(
    single_cst_tree: Callable[[Tree, str], Tree],
    cst_operator_values: Callable[[Tree, str], list[str]],
) -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0
        => (a + b) * 2 <= target
        using Z3
    """

    tree = parse_toetra_code(source)
    parenthesized = single_cst_tree(tree, "parenthesized_scalar")

    assert cst_operator_values(parenthesized, "additive_operator") == ["+"]
    assert cst_operator_values(tree, "multiplicative_operator") == ["*"]


def test_symbolic_division_parses_for_later_capability_analysis(
    cst_operator_values: Callable[[Tree, str], list[str]],
) -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0
        => a / b <= target
        using Z3
    """

    tree = parse_toetra_code(source)

    assert cst_operator_values(tree, "multiplicative_operator") == ["/"]


def test_arithmetic_interval_bounds_parse(
    single_cst_tree: Callable[[Tree, str], Tree],
    cst_operator_values: Callable[[Tree, str], list[str]],
) -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0
        with domain(
            x0.a: [x0.b - 1, x0.b + 1]
        )
        => target <= 7
        using Z3
    """

    tree = parse_toetra_code(source)
    interval = single_cst_tree(tree, "closed_closed_interval")

    assert cst_operator_values(interval, "additive_operator") == ["-", "+"]
