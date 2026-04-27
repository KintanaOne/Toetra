from typing import cast

from lark import Tree

from dsl.ast.nodes.expressions import QuantifierExprNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.fixtures.properties_samples import *


def parse(code: str) -> Tree:
    return parse_forml_code(code)


def test_exists_basic():
    prop = parse_program(parse(VALID_MINIMAL_EXISTS)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, QuantifierExprNode)
    scope = cast(QuantifierExprNode, scope)    

    assert scope.quantifier == "exists"
    assert scope.domain is None
    assert prop.backend is None


def test_exists_with_domain():
    prop = parse_program(parse(VALID_EXISTS_WITH_DOMAIN)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, QuantifierExprNode)
    scope = cast(QuantifierExprNode, scope)    

    domain = scope.domain

    assert scope.quantifier == "exists"
    assert domain is not None
    assert domain.name == "gender"
    assert domain.values == ["male", "female"]