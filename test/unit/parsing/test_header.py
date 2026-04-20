import pytest
from lark import Tree

from forml.parser.parser import parse_forml_code
from previous_forml.ast.queries import (
    get_header,
    get_model_declaration,
    get_target_declaration,
)
from test.fixtures.program_samples import (
    INVALID_HEADER_MISSING_BOTH,
    INVALID_HEADER_MISSING_MODEL,
    INVALID_HEADER_MISSING_TARGET,
    INVALID_HEADER_MODEL_INVALID_TYPE,
    INVALID_HEADER_TARGET_INVALID_TYPE,
    VALID_PROGRAM_WITH_HEADER_COMMENTS,
)
from test.fixtures.properties_samples import VALID_MINIMAL_PAIRWISE

def parse(code: str) -> Tree:
    return parse_forml_code(code)

#----------------------------------------------------------------------------------------------------------------------#

def test_header_valid():

    tree = parse(VALID_MINIMAL_PAIRWISE)

    header = get_header(tree)
    assert header is not None

    model = get_model_declaration(tree)
    target = get_target_declaration(tree)

    assert model is not None
    assert target is not None


def test_header_missing_model():

    with pytest.raises(Exception):
        parse(INVALID_HEADER_MISSING_MODEL)


def test_header_missing_target():

    with pytest.raises(Exception):
        parse(INVALID_HEADER_MISSING_TARGET)


def test_header_missing_both():

    with pytest.raises(Exception):
        parse(INVALID_HEADER_MISSING_BOTH)

def test_header_invalid_model_type():

    with pytest.raises(Exception):
        parse(INVALID_HEADER_MODEL_INVALID_TYPE)

def test_header_invalid_target_type():

    with pytest.raises(Exception):
        parse(INVALID_HEADER_TARGET_INVALID_TYPE)

def test_header_with_comments():

    tree = parse(VALID_PROGRAM_WITH_HEADER_COMMENTS)

    assert get_header(tree) is not None
    assert get_model_declaration(tree) is not None
    assert get_target_declaration(tree) is not None