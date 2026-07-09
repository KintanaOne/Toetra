# test/fixtures/properties_samples.py

# This file contains sample FORML properties used in unit tests for parsing.

# ----------------------------------------------------------------------------------------------------------------------#
#                                             VALID
# ----------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------- AT ---------------------------------------------#

VALID_MINIMAL_AT = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 => CLASSIFICATION.EQUAL()
    """

# AT with neighborhood
VALID_AT_WITH_NEIGHBORHOOD = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """

VALID_AT_WITH_DOMAIN = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 with sex("male","female") => CLASSIFICATION.EQUAL()
    """

# AT with neighborhood and domain
VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) with sex("male","female") => CLASSIFICATION.EQUAL()
    """

# AT with neighborhood and domain and USING clause
VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN_AND_USING = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) with sex("male","female") => CLASSIFICATION.EQUAL() using Z3
    """

# -------------------------------------------- CHECK_AT ---------------------------------------------#

VALID_MINIMAL_CHECK_AT = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.a <= 1
    """

# -------------------------------------------- PAIRWISE ---------------------------------------------#

VALID_MINIMAL_PAIRWISE = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """

VALID_PAIRWISE_WITH_ABSTRACTOR = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() using Z3
    """

# -------------------------------------------- FORALL ---------------------------------------------#

VALID_MINIMAL_FORALL = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall => target == 0
    """


VALID_FORALL_WITH_DOMAIN = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall with gender("male", "female") => target == 0
    """


# -------------------------------------------- EXISTS ---------------------------------------------#

VALID_MINIMAL_EXISTS = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    exists => target == 0
    """


VALID_EXISTS_WITH_DOMAIN = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    exists with gender("male", "female") => target == 0
    """


# ----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID
# ----------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------- AT ---------------------------------------------#

INVALID_AT_MISSING_IDENTIFIER = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at => CLASSIFICATION.EQUAL()
    """


INVALID_AT_INVALID_NEIGHBORHOOD_ARGUMENTS = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2 eps=0.01) => CLASSIFICATION.EQUAL()
    """


INVALID_AT_INVALID_NEIGHBORHOOD_SYNTAX = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 with neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """


INVALID_AT_INVALID_DOMAIN_VALUES = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 with sex(male,female) => CLASSIFICATION.EQUAL()
    """


INVALID_AT_INVALID_DOMAIN_SYNTAX = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in sex("male", "female") => CLASSIFICATION.EQUAL()
    """

# -------------------------------------------- CHECK_AT ---------------------------------------------#

INVALID_CHECK_AT_MISSING_IDENTIFIER = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at => x0.a <= 1
    """


INVALID_CHECK_AT_MISSING_ASSERTION = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
    """


INVALID_CHECK_AT_INVALID_IDENTIFIER = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at 123 => x0.a <= 1
    """

# -------------------------------------------- PAIRWISE ---------------------------------------------#

INVALID_PAIRWISE_MALFORMED_ABSTRACTOR = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() Z3
    """


INVALID_PAIRWISE_MISSING_NEIGHBORHOOD_SYNTAX = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' => CLASSIFICATION.EQUAL() using Z3
    """


INVALID_PAIRWISE_MALFORMED_NEIGHBORHOOD = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2 eps=0.01) => CLASSIFICATION.EQUAL() using Z3
    """


INVALID_PAIRWISE_MISSING_ASSERTION = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) using Z3
    """


INVALID_PAIRWISE_MISSING_IDENTIFIER = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
     ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() using Z3
    """


INVALID_PAIRWISE_MISSING_IDENTIFIER_PRIME = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~  in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() using Z3
    """


INVALID_PAIRWISE_MISSING_BOTH_IDENTIFIERS = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
     ~  in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() using Z3
    """


# ----------------------------------------------------------------------------------------------------------------------#
#                                             EDGE CASES
# ----------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------- AT ---------------------------------------------#


# -------------------------------------------- CHECK_AT ---------------------------------------------#

VALID_CHECK_AT_WITH_COMPLEX_ASSERTION = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.a <= 1 OR x0.b <= 2 AND x0.c <= 3
    """

# -------------------------------------------- PAIRWISE ---------------------------------------------#
