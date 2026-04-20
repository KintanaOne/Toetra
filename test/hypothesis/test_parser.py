from hypothesis import given
from test.hypothesis.settings import DEFAULT_SETTINGS
from test.hypothesis.strategies.program import program

from dsl.parser.parser import parse_forml_code


@DEFAULT_SETTINGS
@given(program())
def test_parser_never_crashes(program):
    try:
        parse_forml_code(program)
    except Exception as e:
        assert False, f"Crash with input:\n{program}\n\nError: {e}"