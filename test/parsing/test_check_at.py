from pathlib import Path

import pytest
from lark import Tree

from forml.ast.queries import (
    get_check_at_expression,
    get_assertion_expression,
    get_identifiers,
    get_identifier_value,
)
from forml.parser.parser import parse_forml_code


def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_check_at_basic():
    """ C1 : Test parsing of a basic check_at expression."""

    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 -> x0.a <= 1
    """

    tree = parse(code)

    check_at_expr = get_check_at_expression(tree)
    identifiers = get_identifiers(check_at_expr)
    assertion = get_assertion_expression(tree)

    assert check_at_expr is not None
    assert len(identifiers) == 1
    assert get_identifier_value(identifiers[0]) == "x0"
    assert assertion is not None


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_check_at_missing_identifier():
    """ C2 : Missing identifier """

    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at -> x0.a <= 1
    """

    with pytest.raises(Exception):
        parse(code)


def test_check_at_missing_assertion():
    """ C3 : Missing assertion """

    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 ->
    """

    with pytest.raises(Exception):
        parse(code)


def test_check_at_with_invalid_identifier():
    """ C4 : Invalid identifier """

    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at 123 -> x0.a <= 1
    """

    with pytest.raises(Exception):
        parse(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             EDGE CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_check_at_with_complex_assertion():
    """ C5 : Complex logical assertion """

    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 ->
        x0.a <= 1 OR x0.b <= 2 AND x0.c <= 3
    """

    tree = parse(code)

    check_at_expr = get_check_at_expression(tree)
    assertion = get_assertion_expression(tree)

    assert check_at_expr is not None
    assert assertion is not None

    # Bonus robuste : vérifier qu'on retrouve bien x0 dans l'expression logique
    identifiers = get_identifiers(assertion)
    values = [get_identifier_value(i) for i in identifiers]

    assert "x0" in values