from __future__ import annotations

from collections.abc import Callable

import pytest
from lark import Token, Tree
from toetra._compiler.parser.errors import ParserError

from toetra._compiler.parser.parser import parse_toetra_code


@pytest.mark.parametrize(
    ("declaration", "expected_rule", "expected_tokens"),
    [
        pytest.param(
            "retry_limit := 7",
            "signed_number_literal",
            ["7"],
            id="PAR-SPC-001-integer",
        ),
        pytest.param(
            "max_risk := 0.20",
            "signed_number_literal",
            ["0.20"],
            id="PAR-SPC-002-float",
        ),
        pytest.param(
            "temperature_floor := -0.1",
            "signed_number_literal",
            ["-", "0.1"],
            id="PAR-SPC-002-signed-float",
        ),
        pytest.param(
            "strict_mode := true",
            "value_boolean",
            ["true"],
            id="PAR-SPC-003-boolean",
        ),
        pytest.param(
            'region_name := "EU"',
            "string",
            ['"EU"'],
            id="PAR-SPC-004-string",
        ),
    ],
)
def test_specification_constant_literal_families_parse(
    declaration: str,
    expected_rule: str,
    expected_tokens: list[str],
    single_cst_tree: Callable[[Tree, str], Tree],
) -> None:
    source = f"""
    model := "credit-risk.joblib"
    target := default_risk

    {declaration}

    [LOGIC]:
    forall applicant => target <= 1 using Z3
    """

    tree = parse_toetra_code(source)
    constant = single_cst_tree(tree, "specification_constant_declaration")
    literal = single_cst_tree(constant, expected_rule)

    tokens = [
        str(token)
        for token in literal.scan_values(lambda value: isinstance(value, Token))
    ]

    assert tokens == expected_tokens


def test_multiple_specification_constants_preserve_source_order_in_cst(
    first_cst_token: Callable[[Tree], Token],
) -> None:
    source = """
    model := "credit-risk.joblib"
    target := default_risk
    dataset := "credit-risk.csv"

    max_risk := 0.20
    minimum_income := 25000.0
    strict_mode := true
    region_name := "EU"

    [LOGIC]:
    forall applicant => target <= max_risk using Z3
    """

    tree = parse_toetra_code(source)
    declarations = list(tree.find_data("specification_constant_declaration"))

    names = [
        str(
            first_cst_token(
                next(
                    child
                    for child in declaration.children
                    if isinstance(child, Tree) and child.data == "identifier"
                )
            )
        )
        for declaration in declarations
    ]

    assert names == [
        "max_risk",
        "minimum_income",
        "strict_mode",
        "region_name",
    ]


def test_legacy_semicolon_separator_remains_parser_compatible() -> None:
    source = """
    model := "credit-risk.joblib"
    target := default_risk

    max_risk := 0.20; minimum_income := 25000.0;

    [LOGIC]:
    forall applicant => target <= max_risk using Z3
    """

    tree = parse_toetra_code(source)

    assert len(list(tree.find_data("specification_constant_declaration"))) == 2


def test_constant_name_in_assertion_remains_unresolved_cst_name(
    single_cst_tree: Callable[[Tree, str], Tree],
    first_cst_token: Callable[[Tree], Token],
) -> None:
    source = """
    model := "credit-risk.joblib"
    target := default_risk

    max_risk := 0.20

    [LOGIC]:
    forall applicant => target <= max_risk using Z3
    """

    tree = parse_toetra_code(source)
    comparison = single_cst_tree(tree, "comparison_expr")
    attributes = list(comparison.find_data("attribute"))

    assert len(attributes) == 1
    assert str(first_cst_token(attributes[0])) == "max_risk"


def test_constant_names_parse_in_interval_bounds(
    cst_operator_values: Callable[[Tree, str], list[str]],
) -> None:
    source = """
    model := "credit-risk.joblib"
    target := default_risk

    minimum_income := 25000.0
    maximum_income := 100000.0

    [LOGIC]:
    forall applicant
        with domain(
            applicant.income: [minimum_income, maximum_income]
        )
        => target <= 1
        using Z3
    """

    tree = parse_toetra_code(source)

    interval_attributes = [
        str(token)
        for attribute in tree.find_data("closed_closed_interval")
        for token in attribute.scan_values(
            lambda value: isinstance(value, Token) and value.type == "IDENTIFIER"
        )
    ]

    assert interval_attributes == ["minimum_income", "maximum_income"]
    assert cst_operator_values(tree, "comparison_operation") == ["<="]


def test_constant_name_parses_as_finite_set_member(
    single_cst_tree: Callable[[Tree, str], Tree],
    first_cst_token: Callable[[Tree], Token],
) -> None:
    source = """
    model := "credit-risk.joblib"
    target := default_risk

    preferred_region := "EU"

    [LOGIC]:
    forall applicant
        with domain(
            applicant.region: {preferred_region, US}
        )
        => target <= 1
        using Z3
    """

    tree = parse_toetra_code(source)
    finite_set = single_cst_tree(tree, "finite_set_domain")
    values = [
        str(first_cst_token(child))
        for child in finite_set.children
        if isinstance(child, Tree) and child.data == "finite_set_value"
    ]

    assert values == ["preferred_region", "US"]


@pytest.mark.parametrize(
    "invalid_declaration",
    [
        pytest.param(
            "annual_limit := monthly_limit * 12",
            id="PAR-SPC-009-derived-expression",
        ),
        pytest.param(
            "max_risk :=",
            id="PAR-SPC-010-missing-value",
        ),
    ],
)
def test_invalid_specification_constant_declarations_are_rejected(
    invalid_declaration: str,
) -> None:
    source = f"""
    model := "credit-risk.joblib"
    target := default_risk

    {invalid_declaration}

    [LOGIC]:
    forall applicant => target <= 1 using Z3
    """

    with pytest.raises(ParserError):
        parse_toetra_code(source)
