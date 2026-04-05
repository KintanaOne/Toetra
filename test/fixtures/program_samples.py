# test/fixtures/program_samples.py

# This file contains sample FORML programs used in unit tests for parsing.

#----------------------------------------------------------------------------------------------------------------------#
#                                             VALIDE
#----------------------------------------------------------------------------------------------------------------------#

VALID_PROGRAM_WITH_HEADER_COMMENTS = """
    # comments are ignored

    model := "model.onnx"
    target := MyTargetColumn

    # between declarations
    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """


VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """

VALID_PROGRAM_WITH_BODY_MULTIPLE_PROPERTIES = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 => CLASSIFICATION.EQUAL()

    [FAIRNESS]:
    forall with gender("male","female") => CLASSIFICATION.EQUAL()
    """


VALID_PROGRAM_WITH_ABSTRACTOR = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() using eran(param1="a")
    """

#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALIDE
#----------------------------------------------------------------------------------------------------------------------#

INVALID_HEADER_MISSING_MODEL = """
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """

INVALID_HEADER_MISSING_TARGET = """
    model := "model.onnx"

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """


INVALID_HEADER_MISSING_BOTH = """
    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """


INVALID_HEADER_MODEL_INVALID_TYPE = """
    model := 123
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """


INVALID_HEADER_TARGET_INVALID_TYPE = """
    model := "model.onnx"
    target := 12345

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL()
    """


INVALID_BODY_EMPTY = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    """

INVALID_BODY_SYNTAX_ERROR = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) CLASSIFICATION.EQUAL()   # missing =>
    """

INVALID_BODY_INVALID_ASSERTION = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.INVALID()
    """


INVALID_BODY_MULTIPLE_EXPRESSION = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall at x0 => CLASSIFICATION.EQUAL()
    """

INVALID_BODY_MISSING_EXPRESSION = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    => CLASSIFICATION.EQUAL()
    """


#----------------------------------------------------------------------------------------------------------------------#
#                                             EDGE CASES
#----------------------------------------------------------------------------------------------------------------------#



