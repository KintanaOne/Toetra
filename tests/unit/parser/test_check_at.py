# tests/unit/parser/test_check_at.py

import pytest

from tests.fixtures.properties_samples import (
    # VALID
    VALID_CHECK_AT_WITH_COMPLEX_ASSERTION,
    VALID_MINIMAL_CHECK_AT,
    # INVALID
    INVALID_CHECK_AT_MISSING_IDENTIFIER,
    INVALID_CHECK_AT_MISSING_ASSERTION,
    INVALID_CHECK_AT_INVALID_IDENTIFIER,
)
from tests.support.parser_programs import (
    assert_check_at_scope,
    assert_no_backend,
    assert_property_basics,
    build_property,
    parse,
)

# ----------------------------------------------------------------------------------------------------------------------
# VALID
# ----------------------------------------------------------------------------------------------------------------------


def test_check_at_basic():

    prop = build_property(VALID_MINIMAL_CHECK_AT)

    scope = assert_check_at_scope(prop)

    assert_property_basics(prop)

    assert scope.variable == "x0"

    assert_no_backend(prop)


def test_check_at_complex_assertion():

    prop = build_property(VALID_CHECK_AT_WITH_COMPLEX_ASSERTION)

    scope = assert_check_at_scope(prop)

    assert_property_basics(prop)

    assert scope.variable == "x0"

    assert_no_backend(prop)


# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------

INVALID_CASES = [
    INVALID_CHECK_AT_MISSING_IDENTIFIER,
    INVALID_CHECK_AT_MISSING_ASSERTION,
    INVALID_CHECK_AT_INVALID_IDENTIFIER,
]


@pytest.mark.parametrize("code", INVALID_CASES)
def test_check_at_invalid(code):

    with pytest.raises(Exception):
        parse(code)
