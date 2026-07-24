# test/unit/parser/test_body.py

import pytest

from test.fixtures.program_samples import (
    INVALID_BODY_EMPTY,
    INVALID_BODY_INVALID_ASSERTION,
    INVALID_BODY_SYNTAX_ERROR,
    VALID_PROGRAM_WITH_BACKEND,
    VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION,
)

from test.unit.parser._program_helpers import (
    assert_backend,
    assert_neighborhood,
    assert_pairwise_scope,
    assert_property_basics,
    build_property,
    parse,
)

# ----------------------------------------------------------------------------------------------------------------------
# VALID
# ----------------------------------------------------------------------------------------------------------------------


def test_body_simple_assertion():

    prop = build_property(VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION)

    scope = assert_pairwise_scope(prop)

    assert_property_basics(prop)

    assert_neighborhood(
        scope.neighborhood,
        "L2",
        eps=0.01,
    )

    assert scope.domain is None


def test_body_with_backend():

    prop = build_property(VALID_PROGRAM_WITH_BACKEND)

    scope = assert_pairwise_scope(prop)

    assert_property_basics(prop)

    assert_neighborhood(
        scope.neighborhood,
        "L2",
        eps=0.01,
    )

    assert_backend(
        prop,
        "eran",
        param1="a",
    )


# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------

INVALID_CASES = [
    INVALID_BODY_EMPTY,
    INVALID_BODY_SYNTAX_ERROR,
    INVALID_BODY_INVALID_ASSERTION,
]


@pytest.mark.parametrize("code", INVALID_CASES)
def test_body_invalid(code):

    with pytest.raises(Exception):
        parse(code)
