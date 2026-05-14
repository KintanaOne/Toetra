# test/unit/parsing/test_forall.py

from test.fixtures.properties_samples import *

from test.unit.parsing.helper import (
    assert_domain,
    assert_no_backend,
    assert_property_basics,
    assert_quantifier_scope,
    build_property,
)


# ----------------------------------------------------------------------------------------------------------------------
# VALID
# ----------------------------------------------------------------------------------------------------------------------

def test_forall_basic():

    prop = build_property(VALID_MINIMAL_FORALL)

    scope = assert_quantifier_scope(prop)

    assert_property_basics(prop)

    assert scope.quantifier == "forall"

    assert scope.domain is None

    assert_no_backend(prop)


def test_forall_with_domain():

    prop = build_property(VALID_FORALL_WITH_DOMAIN)

    scope = assert_quantifier_scope(prop)

    assert_property_basics(prop)

    assert scope.quantifier == "forall"

    assert_domain(
        scope.domain,
        "gender",
        ["male", "female"],
    )

    assert_no_backend(prop)