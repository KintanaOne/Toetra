from pathlib import Path

import pytest
from lark import Tree

from forml.ast.queries import (
    get_pairwise_expression,
    get_neighborhood_dict,
    get_assertion_expression,
    get_abstractor_dict,
    get_identifiers,
    get_identifier_value,
)
from forml.parser.parser import parse_forml_code


def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_pairwise_basic():
    """ PW1 : Basic pairwise expression """

    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    pairwise_expr = get_pairwise_expression(tree)
    neighborhood = get_neighborhood_dict(pairwise_expr)
    assertion = get_assertion_expression(tree)

    identifiers = get_identifiers(pairwise_expr)
    values = [get_identifier_value(i) for i in identifiers]

    assert pairwise_expr is not None
    assert neighborhood is not None
    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == "0.01"
    assert assertion is not None


def test_pairwise_with_using():
    """ PW2 : Pairwise with abstractor """

    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() using Z3
    """

    tree = parse(code)

    pairwise_expr = get_pairwise_expression(tree)
    neighborhood = get_neighborhood_dict(pairwise_expr)
    assertion = get_assertion_expression(tree)
    abstractor = get_abstractor_dict(tree)

    assert pairwise_expr is not None
    assert neighborhood is not None
    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == "0.01"
    assert assertion is not None

    assert abstractor is not None
    assert abstractor["name"] == "Z3"


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_pairwise_missing_using():
    """ PW3 : Missing 'using' keyword """

    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() Z3
    """

    with pytest.raises(Exception):
        parse(code)


def test_pairwise_missing_neighborhood_syntax():
    """ PW4 : Missing neighborhood """

    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' -> CLASSIFICATION.EQUAL() using Z3
    """

    with pytest.raises(Exception):
        parse(code)


def test_pairwise_malformed_neighborhood():
    """ PW5 : Malformed neighborhood """

    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2 eps=0.01) -> CLASSIFICATION.EQUAL() using Z3
    """

    with pytest.raises(Exception):
        parse(code)


def test_pairwise_missing_assertion():
    """ PW6 : Missing assertion """

    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) using Z3
    """

    with pytest.raises(Exception):
        parse(code)


def test_pairwise_missing_identifier():
    """ PW7 : Missing identifier """

    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
     ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() using Z3
    """

    with pytest.raises(Exception):
        parse(code)


def test_pairwise_missing_identifier_prime():
    """ PW8 : Missing identifier prime """

    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~  in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() using Z3
    """

    with pytest.raises(Exception):
        parse(code)


def test_pairwise_missing_both_identifiers():
    """ PW9 : Missing both identifiers """

    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
     ~  in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() using Z3
    """

    with pytest.raises(Exception):
        parse(code)