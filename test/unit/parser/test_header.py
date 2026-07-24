# test/unit/parser/test_header.py

import pytest

from test.fixtures.program_samples import (
    INVALID_HEADER_MISSING_BOTH,
    INVALID_HEADER_MISSING_MODEL,
    INVALID_HEADER_MISSING_TARGET,
    INVALID_HEADER_MODEL_INVALID_TYPE,
    INVALID_HEADER_TARGET_INVALID_TYPE,
    VALID_PROGRAM_WITH_HEADER_COMMENTS,
)

from test.fixtures.properties_samples import (
    VALID_MINIMAL_PAIRWISE,
)

from test.unit.parser._program_helpers import (
    assert_header,
    build_program,
    parse,
)

# ----------------------------------------------------------------------------------------------------------------------
# VALID
# ----------------------------------------------------------------------------------------------------------------------


def test_header_valid():

    program = build_program(VALID_MINIMAL_PAIRWISE)

    assert_header(
        program,
        model="path/to/model.onnx",
        target="MyTargetColumn",
    )


def test_header_with_comments():

    program = build_program(VALID_PROGRAM_WITH_HEADER_COMMENTS)

    assert_header(
        program,
        model="model.onnx",
        target="MyTargetColumn",
    )


# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------

INVALID_CASES = [
    INVALID_HEADER_MISSING_MODEL,
    INVALID_HEADER_MISSING_TARGET,
    INVALID_HEADER_MISSING_BOTH,
    INVALID_HEADER_MODEL_INVALID_TYPE,
    INVALID_HEADER_TARGET_INVALID_TYPE,
]


@pytest.mark.parametrize("code", INVALID_CASES)
def test_header_invalid(code):

    with pytest.raises(Exception):
        parse(code)
