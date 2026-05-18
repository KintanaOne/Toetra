# test/unit/parsing/test_pairwise.py

import pytest

from test.fixtures.properties_samples import (
    INVALID_PAIRWISE_MALFORMED_ABSTRACTOR,
    INVALID_PAIRWISE_MALFORMED_NEIGHBORHOOD,
    INVALID_PAIRWISE_MISSING_ASSERTION,
    INVALID_PAIRWISE_MISSING_BOTH_IDENTIFIERS,
    INVALID_PAIRWISE_MISSING_IDENTIFIER,
    INVALID_PAIRWISE_MISSING_IDENTIFIER_PRIME,
    INVALID_PAIRWISE_MISSING_NEIGHBORHOOD_SYNTAX,
    VALID_MINIMAL_PAIRWISE,
    VALID_PAIRWISE_WITH_ABSTRACTOR,
)

from test.unit.parsing.helper import (
    assert_backend,
    assert_neighborhood,
    assert_no_backend,
    assert_pair,
    assert_pairwise_scope,
    assert_property_basics,
    build_property,
    parse,
)

# ----------------------------------------------------------------------------------------------------------------------
# VALID
# ----------------------------------------------------------------------------------------------------------------------


def test_pairwise_basic():

    prop = build_property(VALID_MINIMAL_PAIRWISE)

    scope = assert_pairwise_scope(prop)

    assert_property_basics(prop)

    assert_pair(
        scope.pair,
        "x",
        "x'",
    )

    assert_neighborhood(
        scope.neighborhood,
        "L2",
        eps=0.01,
    )

    assert scope.domain is None

    assert_no_backend(prop)


def test_pairwise_with_backend():

    prop = build_property(VALID_PAIRWISE_WITH_ABSTRACTOR)

    scope = assert_pairwise_scope(prop)

    assert_property_basics(prop)

    assert_pair(
        scope.pair,
        "x",
        "x'",
    )

    assert_neighborhood(
        scope.neighborhood,
        "L2",
        eps=0.01,
    )

    assert scope.domain is None

    assert_backend(
        prop,
        "Z3",
    )


# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------

INVALID_CASES = [
    INVALID_PAIRWISE_MALFORMED_ABSTRACTOR,
    INVALID_PAIRWISE_MISSING_NEIGHBORHOOD_SYNTAX,
    INVALID_PAIRWISE_MALFORMED_NEIGHBORHOOD,
    INVALID_PAIRWISE_MISSING_ASSERTION,
    INVALID_PAIRWISE_MISSING_IDENTIFIER,
    INVALID_PAIRWISE_MISSING_IDENTIFIER_PRIME,
    INVALID_PAIRWISE_MISSING_BOTH_IDENTIFIERS,
]


@pytest.mark.parametrize("code", INVALID_CASES)
def test_pairwise_invalid(code):

    with pytest.raises(Exception):
        parse(code)
