from pathlib import Path

import pytest
from lark import Tree

from forml.ast.queries import (
    get_at_expression,
    get_domain_dict,
    get_neighborhood_dict,
    get_identifier_value,
    get_identifiers,
)
from forml.parser.parser import parse_forml_code


def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_at_basic():
    """ AT1 : Test parsing of a basic at expression."""

    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    at_expr = get_at_expression(tree)
    identifiers = get_identifiers(at_expr)

    assert at_expr is not None
    assert len(identifiers) == 1
    assert get_identifier_value(identifiers[0]) == "x0"


def test_at_with_neighborhood():
    """ AT2 : Test parsing of an at expression with a neighborhood."""

    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    at_expr = get_at_expression(tree)
    neighborhood = get_neighborhood_dict(at_expr)

    assert at_expr is not None
    assert neighborhood is not None
    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == "0.01"


def test_at_with_domain():
    """ AT3 : Test parsing of an at expression with a domain."""

    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 with sex("male","female") -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    at_expr = get_at_expression(tree)
    domain = get_domain_dict(at_expr)

    assert at_expr is not None
    assert domain is not None
    assert domain["name"] == "sex"
    assert domain["values"] == ["male", "female"]


def test_at_with_neighborhood_and_domain():
    """ AT4 : Test parsing of an at expression with a neighborhood and domain."""

    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) with sex("male","female") -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    at_expr = get_at_expression(tree)
    neighborhood = get_neighborhood_dict(at_expr)
    domain = get_domain_dict(at_expr)

    assert at_expr is not None
    assert neighborhood is not None
    assert domain is not None


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_at_missing_identifier():
    """AT5 — missing identifier"""
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)


def test_at_invalid_neighborhood_arguments():
    """AT6 — malformed neighborhood"""
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2 eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)


def test_at_invalid_neighborhood_syntax():
    """AT7 — malformed neighborhood"""
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 with neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)


def test_at_invalid_domain_value():
    """AT8 — invalid domain value"""
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 with sex(male,female) -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)


def test_at_invalid_domain_syntax():
    """AT9 — invalid domain syntax"""
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in sex("male", "female") -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)