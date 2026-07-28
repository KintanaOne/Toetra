from __future__ import annotations

import pytest
from lark.exceptions import UnexpectedInput

from toetra._compiler.parser.errors import ParserError
from toetra._compiler.parser.parser import parse_toetra_code


def test_parser_normalizes_lark_failure_with_location_and_cause() -> None:
    source = """
model := "model.joblib"
target := score

[LOGIC]:
forall => target <= 7.0
"""

    with pytest.raises(ParserError) as caught:
        parse_toetra_code(source)

    error = caught.value
    assert error.code.startswith("PARSER_")
    assert error.line is not None
    assert error.column is not None
    assert error.hint is not None
    assert isinstance(error.__cause__, UnexpectedInput)
