from typing import cast

import pytest
from lark import Tree

from dsl.ast.nodes.expressions import CheckAtExprNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.fixtures.properties_samples import *


def parse(code: str) -> Tree:
    return parse_forml_code(code)


def test_check_at_basic():
    prop = parse_program(parse(VALID_MINIMAL_CHECK_AT)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, CheckAtExprNode)
    scope = cast(CheckAtExprNode, scope)
    
    assert scope.variable == "x0"
    assert prop.rule.assertion is not None


@pytest.mark.parametrize("code", [
    INVALID_CHECK_AT_MISSING_IDENTIFIER,
    INVALID_CHECK_AT_MISSING_ASSERTION,
    INVALID_CHECK_AT_INVALID_IDENTIFIER,
])
def test_check_at_invalid(code):
    with pytest.raises(Exception):
        parse(code)


def test_check_at_complex_assertion():
    prop = parse_program(parse(VALID_CHECK_AT_WITH_COMPLEX_ASSERTION)).body[0]

    assert prop.rule.assertion is not None