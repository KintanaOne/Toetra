# test/fixtures/logic_samples.py
# This file contains sample logic properties for testing purposes.

# ----------------------------------------------------------------------------------------------------------------------#
#                                             BASE
# ----------------------------------------------------------------------------------------------------------------------#

SIMPLE_LOGIC_PROPERTY = """
    model := "path/to/model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 => A==0 AND B==1
    """

SIMPLE_PROBLEM_PROPERTY = """
    model := "path/to/model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 => CLASSIFICATION.EQUAL()
    """


# ----------------------------------------------------------------------------------------------------------------------#
#                                             PRECEDENCE
# ----------------------------------------------------------------------------------------------------------------------#

OPERATOR_PRECEDENCE_PROPERTY = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.a <= 1 OR x0.b <= 2 AND x0.c <= 3
    """


PARENTHESES_PRECEDENCE_PROPERTY = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => (x0.a <= 1 OR x0.b <= 2) AND x0.c <= 3
    """


NOT_PRECEDENCE_PROPERTY = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
        NOT x0.a <= 1 AND x0.b <= 2
    """


# ----------------------------------------------------------------------------------------------------------------------
#                                             IMPLICATION
# ----------------------------------------------------------------------------------------------------------------------

SIMPLE_LOGIC_IMPLICATION_PROPERTY = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
        x0.a <= 1 -> x0.b <= 2
    """


NESTED_IMPLICATION_PROPERTY = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
        x0.a <= 1 -> x0.b <= 2 -> x0.c <= 3
    """

# ----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID
# ----------------------------------------------------------------------------------------------------------------------#

INVALID_LOGIC_SYNTAX = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
    x0.a <= OR x0.b <= 2
    """


INVALID_PARENTHESES = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
    (x0.a <= 1 OR x0.b <= 2
    """

# ----------------------------------------------------------------------------------------------------------------------#
#                                             COMPLEX VALID
# ----------------------------------------------------------------------------------------------------------------------#

VALID_TRIPLE_OR_PROPERTY = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
        x0.a <= 1 OR x0.b <= 2 OR x0.c <= 3
    """


VALID_TRIPLE_AND_PROPERTY = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
        x0.a <= 1 AND x0.b <= 2 AND x0.c <= 3
    """

VALID_IMPLICATION_PROPERTY = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
        x0.a <= 1 -> x0.b <= 2
    """
