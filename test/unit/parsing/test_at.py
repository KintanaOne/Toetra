# test/unit/parsing/test_at.py

import pytest

from test.fixtures.properties_samples import *

from test.unit.parsing.helper import (
    assert_at_scope,
    assert_domain,
    assert_neighborhood,
    assert_no_backend,
    assert_property_basics,
    build_property,
    parse,
)


# ----------------------------------------------------------------------------------------------------------------------
# VALID
# ----------------------------------------------------------------------------------------------------------------------

def test_at_basic():

    prop = build_property(VALID_MINIMAL_AT)

    scope = assert_at_scope(prop)

    assert_property_basics(prop)

    assert scope.variable == "x0"

    assert scope.neighborhood is None
    assert scope.domain is None

    assert_no_backend(prop)


def test_at_with_neighborhood():

    prop = build_property(VALID_AT_WITH_NEIGHBORHOOD)

    scope = assert_at_scope(prop)

    assert_property_basics(prop)

    assert_neighborhood(
        scope.neighborhood,
        "L2",
        eps=0.01,
    )

    assert scope.domain is None

    assert_no_backend(prop)


def test_at_with_domain():

    prop = build_property(VALID_AT_WITH_DOMAIN)

    scope = assert_at_scope(prop)

    assert_property_basics(prop)

    assert_domain(
        scope.domain,
        "sex",
        ["male", "female"],
    )

    assert scope.neighborhood is None

    assert_no_backend(prop)


def test_at_with_neighborhood_and_domain():

    prop = build_property(
        VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN
    )

    scope = assert_at_scope(prop)

    assert_property_basics(prop)

    assert_neighborhood(
        scope.neighborhood,
        "L2",
        eps=0.01,
    )

    assert_domain(
        scope.domain,
        "sex",
        ["male", "female"],
    )

    assert_no_backend(prop)


# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------

INVALID_CASES = [
    INVALID_AT_MISSING_IDENTIFIER,
    INVALID_AT_INVALID_NEIGHBORHOOD_ARGUMENTS,
    INVALID_AT_INVALID_NEIGHBORHOOD_SYNTAX,
    INVALID_AT_INVALID_DOMAIN_VALUES,
    INVALID_AT_INVALID_DOMAIN_SYNTAX,
]


@pytest.mark.parametrize("code", INVALID_CASES)
def test_at_invalid(code):

    with pytest.raises(Exception):
        parse(code)