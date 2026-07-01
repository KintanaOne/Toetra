from typing import cast

import pytest
from lark import Tree

from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    PairwiseExprNode,
    QuantifierExprNode,
)
from dsl.builder.program import parse_program
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.properties import EnumProperty
from dsl.parser.parser import parse_forml_code

from test.fixtures.program_samples import (
    INVALID_BODY_MISSING_EXPRESSION,
    INVALID_BODY_MULTIPLE_EXPRESSION,
    VALID_PROGRAM_WITH_BODY_MULTIPLE_PROPERTIES,
)

from test.fixtures.properties_samples import (
    VALID_AT_WITH_NEIGHBORHOOD,
    VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN,
    VALID_FORALL_WITH_DOMAIN,
    VALID_MINIMAL_CHECK_AT,
    VALID_PAIRWISE_WITH_ABSTRACTOR,
)

# ----------------------------------------------------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------------------------------------------------


def parse(code: str) -> Tree:
    return parse_forml_code(code)


def build_program(code: str):
    return parse_program(parse(code))


# ----------------------------------------------------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------------------------------------------------


def test_program_header():

    program = build_program(VALID_AT_WITH_NEIGHBORHOOD)

    header = program.header

    assert header is not None
    assert header.model == "model.onnx"
    assert header.target == "MyTarget"


# ----------------------------------------------------------------------------------------------------------------------
# AT
# ----------------------------------------------------------------------------------------------------------------------


def test_program_with_at():

    prop = build_program(VALID_AT_WITH_NEIGHBORHOOD).body[0]

    scope = prop.rule.scope

    assert isinstance(scope, AtExprNode)
    scope = cast(AtExprNode, scope)

    neighborhood = scope.neighborhood

    assert prop.type == EnumProperty.ROBUSTNESS
    assert prop.rule.assertion is not None

    assert neighborhood is not None
    assert neighborhood.metric == "L2"
    assert neighborhood.args[0].key == "eps"
    assert neighborhood.args[0].value == 0.01

    assert prop.backend is None


# ----------------------------------------------------------------------------------------------------------------------
# CHECK_AT
# ----------------------------------------------------------------------------------------------------------------------


def test_program_with_check_at():

    prop = build_program(VALID_MINIMAL_CHECK_AT).body[0]

    scope = prop.rule.scope

    assert isinstance(scope, CheckAtExprNode)
    scope = cast(CheckAtExprNode, scope)

    assert prop.type == EnumProperty.ROBUSTNESS
    assert scope.variable == "x0"
    assert prop.rule.assertion is not None

    assert prop.backend is None


# ----------------------------------------------------------------------------------------------------------------------
# PAIRWISE
# ----------------------------------------------------------------------------------------------------------------------


def test_program_with_pairwise():

    prop = build_program(VALID_PAIRWISE_WITH_ABSTRACTOR).body[0]

    scope = prop.rule.scope

    assert isinstance(scope, PairwiseExprNode)
    scope = cast(PairwiseExprNode, scope)

    neighborhood = scope.neighborhood

    assert prop.type == EnumProperty.ROBUSTNESS
    assert prop.rule.assertion is not None

    assert neighborhood is not None
    assert neighborhood.metric == "L2"
    assert neighborhood.args[0].key == "eps"
    assert neighborhood.args[0].value == 0.01

    assert prop.backend is not None
    assert prop.backend.name == EnumBackend.Z3


# ----------------------------------------------------------------------------------------------------------------------
# QUANTIFIER
# ----------------------------------------------------------------------------------------------------------------------


def test_program_with_quantifier():

    prop = build_program(VALID_FORALL_WITH_DOMAIN).body[0]

    scope = prop.rule.scope

    assert isinstance(scope, QuantifierExprNode)
    scope = cast(QuantifierExprNode, scope)

    domain = scope.domain

    assert prop.type == EnumProperty.ROBUSTNESS
    assert prop.rule.assertion is not None

    assert domain is not None
    assert domain.name == "gender"
    assert domain.values == ["male", "female"]

    assert prop.backend is None


# ----------------------------------------------------------------------------------------------------------------------
# MULTIPLE PROPERTIES
# ----------------------------------------------------------------------------------------------------------------------


def test_program_multiple_properties():

    program = build_program(VALID_PROGRAM_WITH_BODY_MULTIPLE_PROPERTIES)

    assert len(program.body) == 2

    assert isinstance(program.body[0].rule.scope, AtExprNode)
    assert isinstance(program.body[1].rule.scope, QuantifierExprNode)


# ----------------------------------------------------------------------------------------------------------------------
# DOMAIN + NEIGHBORHOOD
# ----------------------------------------------------------------------------------------------------------------------


def test_program_with_domain_and_neighborhood():

    prop = build_program(VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN).body[0]

    scope = prop.rule.scope

    assert isinstance(scope, AtExprNode)
    scope = cast(AtExprNode, scope)

    neighborhood = scope.neighborhood
    domain = scope.domain

    assert prop.type == EnumProperty.ROBUSTNESS
    assert prop.rule.assertion is not None

    assert neighborhood is not None
    assert neighborhood.metric == "L2"
    assert neighborhood.args[0].key == "eps"
    assert neighborhood.args[0].value == 0.01

    assert domain is not None
    assert domain.name == "sex"
    assert domain.values == ["male", "female"]

    assert prop.backend is None


# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------


def test_invalid_multiple_expr():

    with pytest.raises(Exception):
        parse(INVALID_BODY_MULTIPLE_EXPRESSION)


def test_invalid_missing_expr():

    with pytest.raises(Exception):
        parse(INVALID_BODY_MISSING_EXPRESSION)
