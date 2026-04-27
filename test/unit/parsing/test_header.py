import pytest
from lark import Tree

from dsl.builder.header import get_header, parse_header
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
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
    program = parse_program(tree)
    header = program.header
    
    assert header is not None

    model = header.model
    target = header.target

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
    program = parse_program(tree)
    header = program.header
    
    assert header is not None
    assert header.model is not None
    assert header.target is not None
    assert header.model == "model.onnx"
    assert header.target == "MyTargetColumn"
