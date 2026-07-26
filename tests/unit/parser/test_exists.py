# tests/unit/parser/test_exists.py


from tests.fixtures.properties_samples import (
    # VALID
    VALID_EXISTS_WITH_DOMAIN,
    VALID_MINIMAL_EXISTS,
)
from tests.support.parser_programs import (
    assert_domain,
    assert_no_backend,
    assert_property_basics,
    assert_quantifier_scope,
    build_property,
)

# ----------------------------------------------------------------------------------------------------------------------
# VALID
# ----------------------------------------------------------------------------------------------------------------------


def test_exists_basic():

    prop = build_property(VALID_MINIMAL_EXISTS)

    scope = assert_quantifier_scope(prop)

    assert_property_basics(prop)

    assert scope.quantifier == "exists"

    assert scope.domain is None

    assert_no_backend(prop)


def test_exists_with_domain():

    prop = build_property(VALID_EXISTS_WITH_DOMAIN)

    scope = assert_quantifier_scope(prop)

    assert_property_basics(prop)

    assert scope.quantifier == "exists"

    assert_domain(
        scope.domain,
        "gender",
        ["male", "female"],
    )

    assert_no_backend(prop)
