from lark import UnexpectedToken
import pytest
from forml.parser.errors import ParserHeaderError, ParserHeaderModelError
from forml.parser.parser import parse_forml_code
from test.utils import *


def test_header_correct_order():
    code = """
    '''
    Le header respecte l'ordre :
        - model_declaration
        - target_declaration
    '''
    model := "path/to/model.onnx"
    target := MyTargetColumn

    # 1 forall without using
    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
    """
    result = parse_forml_code(code)

    # check that result is a Tree
    assert isinstance(result, Tree)

    # check that header is present
    header = find_child(result, "header")
    assert header is not None, "Header not found in the parsed result"

    # check that header contains model_declaration and target_declaration
    model_decl = find_child(header, "model_declaration")
    target_decl = find_child(header, "target_declaration")

    assert model_decl is not None, "Model declaration not found in header"
    assert target_decl is not None, "Target declaration not found in header"

    # check order of declarations in header
    model_index = header.children.index(model_decl)
    target_index = header.children.index(target_decl)
    assert model_index < target_index, "Model declaration should come before target declaration"


def test_header_uncorrect_order():
    code = """
    '''
    Le header ne respecte pas l'ordre :
        - model_declaration
        - target_declaration
    '''
    target := MyTargetColumn
    model := "path/to/model.onnx"

    # 1 forall without using
    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
    """

    try:
        parse_forml_code(code)
        pytest.fail("An exception should have been raised, but parsing succeeded")
    except Exception as exc:
        print("\n\n=== Exception raised ===")
        print(type(exc), exc)
        print("========================\n\n")


def test_header_with_comments():
    code = '''
    # This is a comment
    # Another comment
    model := "path/to/model.onnx"
    target := MyTargetColumn

    # 1 forall without using
    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
    '''
    # Le parsing doit réussir même avec des commentaires ignorés
    result = parse_forml_code(code)

    # Vérifier que le header est présent
    header = find_child(result, "header")
    assert header is not None, "Header not found in the parsed result"

    # Vérifier que le header contient model_declaration et target_declaration
    model_decl = find_child(header, "model_declaration")
    target_decl = find_child(header, "target_declaration")

    assert model_decl is not None
    assert target_decl is not None



def test_header_missing_model():
    code = """
    '''
    Le header ne respecte pas l'ordre :
        - model_declaration
        - target_declaration
    '''
    target := MyTargetColumn

    # 1 forall without using
    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
    """

    with pytest.raises(UnexpectedToken) as exc_info:
        parse_forml_code(code)

    assert "model" in str(exc_info.value).lower()

def test_header_missing_target():
    code = """
    '''
    Le header ne respecte pas l'ordre :
        - model_declaration
        - target_declaration
    '''
    model := "path/to/model.onnx"

    # 1 forall without using
    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
    """

    with pytest.raises(UnexpectedToken) as exc_info:
        parse_forml_code(code)

    assert "target" in str(exc_info.value).lower()


def test_header_invalid_model_type():
    code = '''
    # This is a comment
    # Another comment
    model := 123
    target := MyTargetColumn

    
    # 1 forall without using
    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
    '''
    try:
        parse_forml_code(code)
        pytest.fail("model declaration with invalid type should raise an exception")
    except Exception as exc:
        print("\n\n=== Exception raised ===")
        print(type(exc), exc)
        print("========================\n\n")



def test_header_invalid_target_type():
    code = '''
    model := "path/to/model.onnx"
    target := 123

    
    # 1 forall without using
    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
    '''

    try:
        parse_forml_code(code)
        pytest.fail("target declaration with invalid type should raise an exception")
    except Exception as exc:
        print("\n\n=== Exception raised ===")
        print(type(exc), exc)
        print("========================\n\n")
